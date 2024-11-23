# SPATS Personal Asset Tracking Software
This is the frontend for SPATS. This just displays the info that the SPATS Backend stores and manages.

## Endpoints
`/` - Display api endpoint info  
`/asset` - Get list of all asset types available  
`/asset/<string:_id>` - Get info about specific asset  
`/asset/<string:_id>/edit` - Edit asset type  
`/asset/<string:_id>/new` - Create new thing of asset type  
`/asset/new` - Create new asset type  
`/thing` - List all things  
`/thing/<string:_id>` - Get info about specific thing  
`/thing/<string:_id>/edit` - Edit specific thing  
`/thing/asset/<string:_id>` - List all things of asset type  
`/combo` - Get list of all combo types available  
`/combo/<string:_id>` - Get info about specific combo  
`/combo/<string:_id>/edit` - Edit combo type  
`/combo/<string:_id>/new` - Create new thing of combo type  
`/combo/new` - Create new combo type  
`/group` - List all groups  
`/group/<string:_id>` - Get info about specific group  
`/group/<string:_id>/edit` - Edit specific group  
`/group/combo/<string:_id>` - List all groups of combo type  

## License
[MIT License](https://opensource.org/licenses/MIT)
