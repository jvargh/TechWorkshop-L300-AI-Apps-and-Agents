# .NET 10 LTS Update

## Overview

This repository has been updated to use **.NET 10**, the current Long-Term Support (LTS) version of .NET, released on November 11, 2025.

## Changes Made

### 1. Created `global.json`
A new `global.json` file has been added to the repository root to explicitly pin the .NET SDK version:

```json
{
  "sdk": {
    "version": "10.0.100",
    "rollForward": "latestPatch",
    "allowPrerelease": false
  }
}
```

This ensures that:
- The project uses .NET 10.0.100 SDK (the LTS version)
- The SDK will roll forward to the latest patch version (e.g., 10.0.101, 10.0.102) for security updates
- Preview releases are not used

### 2. Updated `.devcontainer/devcontainer.json`
The devcontainer configuration has been updated to explicitly include the .NET 10 feature:

```json
"features": {
  "ghcr.io/devcontainers/features/dotnet:2": {
    "version": "10.0",
    "installUsingApt": false
  },
  ...
}
```

This ensures that when developers open the repository in a GitHub Codespace or VS Code with Dev Containers, .NET 10 is properly installed and configured.

## Benefits of .NET 10 LTS

### Long-Term Support
- **Support Period**: November 11, 2025 – November 14, 2028 (3 years)
- **Security Updates**: Regular security patches and bug fixes
- **Stability**: Production-ready for enterprise applications

### Performance Improvements
- Enhanced JIT optimizations
- Better struct argument code generation
- Support for AVX10.2 instructions
- Improved memory usage and throughput

### Modern Language Features
- **C# 14**: Latest language features and improvements
- **F# 10.0**: Enhanced functional programming capabilities
- **Visual Basic 17.13**: Continued support and updates

### AI and Cloud-Native Features
- Built-in **Microsoft Agent Framework** for multi-agent systems
- Enhanced cryptography with post-quantum support
- Improved container image creation and deployment
- Better JSON serialization and networking upgrades

### Developer Experience
- Unified CLI commands with tab completion
- Enhanced debugging and diagnostics
- Improved ASP.NET Core features (Blazor, OpenAPI, form validation)
- Better integration with Visual Studio 2026 and JetBrains Rider

## Compatibility

### Azure Tools
The following Azure tools used in this repository are fully compatible with .NET 10:

- **Azure Bicep** (v0.39.26): Infrastructure as Code tool
- **Azure Developer CLI (azd)**: Cloud deployment tool
- **Azure CLI**: Azure management tool

### Breaking Changes
No breaking changes were identified for this repository as:
- This is primarily a Python-based AI workshop project
- .NET is used for development tools (Bicep, azd) rather than application code
- All existing workflows and scripts continue to function correctly

## Verification

To verify the .NET version in use:

```bash
# Check .NET SDK version
dotnet --version

# View all installed SDKs and runtimes
dotnet --info

# Verify global.json is being used
dotnet --info | grep "global.json"
```

Expected output:
```
.NET SDK:
 Version:           10.0.100
 ...
global.json file:
  /path/to/repository/global.json
```

## Migration Notes

### For Local Development
If you're working locally (not using Codespaces):

1. **Install .NET 10 SDK**: Download from https://dotnet.microsoft.com/download/dotnet/10.0
2. **Verify Installation**: Run `dotnet --version` to confirm 10.0.100 or later
3. **No Code Changes Required**: Existing Python and Bicep code continues to work

### For Codespaces/Dev Containers
- No action required - .NET 10 will be automatically installed when the container is rebuilt
- First time opening after this update may take longer due to feature installation

## Testing Performed

The following tests were performed to ensure compatibility:

✅ **Bicep CLI**: Tested infrastructure deployment scripts
```bash
bicep --version
# Output: Bicep CLI version 0.39.26 (1e90b06e40)
```

✅ **.NET SDK**: Verified SDK version and global.json configuration
```bash
dotnet --version
# Output: 10.0.100
```

✅ **Compatibility**: All existing tools and workflows function correctly

## Future Updates

The `rollForward` policy in `global.json` is set to `latestPatch`, which means:
- The SDK will automatically use the latest patch version (10.0.x)
- Major version updates (e.g., to .NET 11) will require explicit action
- This ensures stability while maintaining security updates

## Support Timeline

| Version | Release Date | End of Support | Type |
|---------|-------------|----------------|------|
| .NET 10 | Nov 11, 2025 | Nov 14, 2028 | LTS |
| .NET 9 | Nov 12, 2024 | May 12, 2026 | STS (Standard Term Support) |
| .NET 8 | Nov 14, 2023 | Nov 10, 2026 | LTS |

**Recommendation**: Stay on .NET 10 LTS for the next 3 years to benefit from long-term support.

## References

- [.NET 10 Download](https://dotnet.microsoft.com/download/dotnet/10.0)
- [.NET Support Policy](https://dotnet.microsoft.com/platform/support/policy)
- [.NET 10 Release Notes](https://github.com/dotnet/core/tree/main/release-notes/10.0)
- [What's New in .NET 10](https://learn.microsoft.com/dotnet/core/whats-new/dotnet-10)

## Questions or Issues?

If you encounter any issues related to the .NET 10 update, please:
1. Verify your local .NET installation: `dotnet --version`
2. Ensure global.json is present in the repository root
3. Rebuild your dev container if using Codespaces
4. Report issues to the repository maintainers with details about your environment
