Changelog for Solgema.FlowView
------------------------------
1.0.8
-----
- Whole javascript refactored. lighter and better handling of multiple flowview on a page.

1.0.7
.....
- Add extra current class to standard tabs (fade, ...)
- remove allowAnonymousShowAbout

1.0.6
-----
- Remove the automatic marker for IFlowViewMarker as it causes CSRF protection issues
- Remove IFlowViewMarkerDX not used.
- Added uninstall profile for Plone 5

1.0.5
-----
- Use plone.app.contenttypes' FolderView as base for FlowView view as we use "folder_listing" in the template.


1.0.4
-----

- Fix getting portal catalog on brain item, use getSiteUI instead

- Fix errors when Martronic.ContentImageExtend is not installed

- 1.0.3 : Fix Plone5 collection. added field for navigation buttons custom class

- 1.0.2 : Fix missing file in dx directory (Plone 5 Dexterity) [fmoret]

- 1.0.1 : Python version

Solgema.FlowView - 0.1 Unreleased

    - Initial package structure.
      [zopeskel]

