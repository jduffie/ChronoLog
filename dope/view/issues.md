
# DOPE View UI Issues 

# Session filters - ✅ RESOLVED
~~When I select one of the rows in the session table, the Filter section opens up as if I had selected the dropdown for it to appear.~~ - Fixed auto-opening issue by removing forced expander state


# Session table - ✅ RESOLVED
~~should not include a column for UUID~~
- UUID column removed from sessions table display

# Session Details - ✅ RESOLVED

 * ~~should not have a Duplicate button~~ - Duplicate button removed
 * ~~should use units according to user preferences~~ - Unit system integration implemented throughout
 * ~~should not have this text - 'Archive functionality is no longer available'~~ - Archive text removed

## Session Info - ✅ RESOLVED

* ~~Data Sources: - The values should appear as a subset of this text - you could offset them to the right, use bold or other means~~ - Implemented with 4-space indentation and proper formatting
* ~~Chronograph and Weather it should provide the name and not say "Linked". Examples:~~ - Fixed to show actual names:
  * Chronograph source: should be the name of the actual chronograph source
  * ~~Weather source: J35700~~ - Now shows weather source name or "Not-linked"

* ~~should not have this text - '🕐 Session Times:'~~ - Emoji text removed

* ~~tab should not have UUIDs as seen here~~ - UUIDs replaced with meaningful names:
  * ~~Session ID: e1c4150a-43f8-47e0-9a40-9f8ca45badb2~~ - Now shows meaningful session info
  * ~~Cartridge ID: 42df6ee4-e2bb-405d-afab-2ed2ea9b3f60~~ - Now shows cartridge name
  * ~~Chrono Session ID: 53bbdc75-3605-4b74-a130-4027b3b51335~~ - Now shows chronograph name

 * ~~Session Info should include name, start time, and end time~~ - Implemented

 * ~~Session Info should ALSO include a single reference to all the data sources:~~ - Implemented:
   * ~~Chronograph - name~~ - Shows "Linked" or "Not-linked"
   * ~~Weather - name - name of weather source or not-linked if not available~~ - Shows weather source name or "Not-linked"
   * ~~Range - name~~ - Shows range name
   * ~~Bullet - display name~~ - Shows bullet display name
   * ~~Cartridge - display name~~ - Shows cartridge display name
   * ~~Rifle - name~~ - Shows rifle name

 * ~~remove anything else not listed above~~ - Cleaned up to show only required information

## Range tab - ✅ RESOLVED

* ~~Azimuth: 189.29° -> should say "Azimuth Angle: 189.29°"~~ - Fixed to show "Azimuth Angle:" label
* ~~Remove "Distance: 910.5m"~~ - Distance field removed from Range tab

* ~~create a Range tab, it should come after Session Info. It should include the following data:~~ - Created Range tab with all required data:
  * ~~Lat/Lon - and a hyperlink to google maps~~ - Implemented with Google Maps hyperlink
  * ~~Altitude~~ - Shows altitude in meters
  * ~~Azimuth and Elevation angles~~ - Shows both angles with proper formatting
  

## Rifle tab - ✅ RESOLVED
 * ~~should not have UUIDs as seen here~~ - Rifle ID UUID removed
   * ~~Rifle ID: 6d5d6a54-f5dc-4020-9d9f-cc282412c5aa~~

## Bullet tab - ✅ RESOLVED
 * ~~should group the following measurements together~~ - Physical measurements grouped:
   * Length ✅
   * Diameter (Land) ✅
   * Diameter (Groove) ✅
 * ~~should group the following together~~ - Ballistic coefficients grouped:
   * BC G1 ✅
   * BC G7 ✅

## Weather tab - ✅ RESOLVED
 * ~~Units are in metric - ensure units align with user prefs~~ - Unit system now follows user preferences for all weather data
 * ~~Group the Wind measurements together on the right side~~ - Wind measurements grouped together on right side
 * ~~should provide the name of the Weather Source instead of the UUID~~ - Weather Source name displayed
   * ~~Weather Source: 0674bd48-b740-4e61-bc46-fd8d5abd39c2~~

 * ~~does not show Wind Speed 2 b/c its missing in the schema~~ - Wind Speed 2 field added to model, table, and UI

## Shots tab - ✅ RESOLVED
 * ~~missing row selector - should let user select a single row and then render all values for that row beneath the table~~ - Added Select Mode tab with single-row selection and detailed shot information display beneath table
 * ~~is missing a selector to let user pick what columns to show~~ - Column chooser added





