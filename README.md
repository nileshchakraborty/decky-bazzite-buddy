# Bazzite Buddy

## Overview
This plugin provides useful Bazzite actions and release information in the Decky quick access menu.

## Features
- Fetch and display the latest Bazzite release notes.
- Refresh the changelog with a single click.
- Direct link to view all release notes on GitHub.
- Restart directly to Windows for one boot when an exact Windows Boot Manager
  EFI entry is available.
- Simple and responsive user interface.

## How to Use
1. Install the plugin by downloading the zip file from the releases tab, then
   selecting 'install from zip file' in decky loader settings page. (note,
   currently downloading from the github url does not seem to work properly, I
   am investigating)
2. Open the plugin from the Decky menu to view the latest release notes.
3. Use the provided buttons to refresh the changelog or navigate to the GitHub releases page.
4. On dual-boot systems, use **Restart to Windows** in the Power section and
   confirm the restart. The action is hidden when Windows Boot Manager cannot be
   detected.

## Requirements
- Decky Loader installed on your system.
- Internet connection to fetch changelogs.
