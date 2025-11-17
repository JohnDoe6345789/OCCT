#!/usr/bin/env python3
"""
Main conversion orchestration script.

Coordinates the conversion of OCCT C/C++ files to Python.
Usage:
    python conversion_runner.py [--module MODULE] [--toolkit TOOLKIT] [--analyze]
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from cpp_parser import SourceAnalyzer, CppHeaderParser
from python_generator import PythonClassGenerator, DirectoryStructureGenerator


def analyze_source_structure(src_root: Path) -> None:
    """Analyze and print OCCT source structure."""
    analyzer = SourceAnalyzer(src_root)
    modules = analyzer.analyze()
    
    print("\n" + "=" * 70)
    print("OCCT SOURCE STRUCTURE ANALYSIS")
    print("=" * 70)
    
    total_files = 0
    for module, toolkits in sorted(modules.items()):
        module_total = sum(len(files) for files in toolkits.values())
        total_files += module_total
        print(f"\n{module}: {len(toolkits)} toolkits, {module_total} files")
        
        for toolkit, files in sorted(toolkits.items()):
            print(f"  - {toolkit}: {len(files)} header files")
    
    print(f"\nTotal files to convert: {total_files}")
    print("\nConversion Priority Order:")
    print("-" * 70)
    
    priority = analyzer.get_priority_order()
    for i, (module, toolkit, files) in enumerate(priority, 1):
        print(f"{i}. {module:30s} / {toolkit:20s} ({len(files)} files)")
    
    print("=" * 70 + "\n")


def convert_module(
    src_root: Path,
    output_root: Path,
    module: str,
    toolkit: str,
    dry_run: bool = False
) -> None:
    """Convert a specific module/toolkit."""
    print(f"\nConverting {module}/{toolkit}...")
    
    analyzer = SourceAnalyzer(src_root)
    modules = analyzer.analyze()
    
    if module not in modules or toolkit not in modules[module]:
        print(f"ERROR: {module}/{toolkit} not found!")
        return
    
    header_files = modules[module][toolkit]
    print(f"Found {len(header_files)} header files")
    
    # Create output structure
    toolkit_output = output_root / module.lower() / toolkit.lower()
    toolkit_output.mkdir(parents=True, exist_ok=True)
    
    # Parse each header file
    for i, header_path in enumerate(header_files, 1):
        print(f"  [{i}/{len(header_files)}] Processing {header_path.name}...", end=" ", flush=True)
        
        try:
            parser = CppHeaderParser(header_path)
            classes = parser.parse()
            
            if not classes:
                print("(no classes found)")
                continue
            
            print(f"({len(classes)} classes)")
            
            # Generate Python files for each class
            for class_name, cpp_class in classes.items():
                # Create package directory
                package_name = header_path.parent.name
                pkg_dir = DirectoryStructureGenerator.create_package_structure(
                    output_root,
                    module,
                    toolkit,
                    package_name
                )
                
                # Generate Python file
                py_filename = pkg_dir / f"{class_name.lower()}.py"
                
                if not dry_run:
                    generator = PythonClassGenerator(output_root, cpp_class)
                    generator.save(py_filename)
                    print(f"    -> {py_filename.relative_to(output_root)}")
        
        except Exception as e:
            print(f"ERROR: {e}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OCCT to Python Conversion Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python conversion_runner.py --analyze
    Show source structure analysis
  
  python conversion_runner.py --module FoundationClasses --toolkit TKernel
    Convert FoundationClasses/TKernel to Python
  
  python conversion_runner.py --module FoundationClasses --toolkit TKernel --dry-run
    Show what would be converted without writing files
        """
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze source structure and exit'
    )
    parser.add_argument(
        '--module',
        type=str,
        help='Module to convert (e.g., FoundationClasses)'
    )
    parser.add_argument(
        '--toolkit',
        type=str,
        help='Toolkit to convert (e.g., TKernel)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without writing files'
    )
    parser.add_argument(
        '--src-root',
        type=Path,
        default=Path(__file__).parent.parent / 'src',
        help='Path to OCCT src directory'
    )
    parser.add_argument(
        '--output-root',
        type=Path,
        default=Path(__file__).parent.parent / 'python_port',
        help='Output directory for Python ports'
    )
    
    args = parser.parse_args()
    
    # Validate paths
    if not args.src_root.exists():
        print(f"ERROR: Source root not found: {args.src_root}")
        return 1
    
    # Handle analyze mode
    if args.analyze:
        analyze_source_structure(args.src_root)
        return 0
    
    # Handle conversion mode
    if args.module and args.toolkit:
        convert_module(
            args.src_root,
            args.output_root,
            args.module,
            args.toolkit,
            dry_run=args.dry_run
        )
        return 0
    
    # If neither analyze nor conversion specified, show analysis
    if not args.module and not args.toolkit:
        print("Use --analyze to show structure, or specify --module and --toolkit")
        parser.print_help()
        return 1
    
    print("ERROR: Both --module and --toolkit are required for conversion")
    return 1


if __name__ == '__main__':
    sys.exit(main())
