# SPATS Personal Asset Tracking Software
This is the frontend for SPATS. This just displays the info that the SPATS Backend stores and manages.

## Endpoints
`/` - Root  
`/asset` - Get list of all asset types available  
`/asset/<asset:suid>` - Get info about specific asset  
`/asset/<asset:suid>/edit` - Edit asset type  
`/asset/<asset:suid>/new` - Create new thing of asset type  
`/asset/new` - Create new asset type  
`/thing` - Redirects to `/thing/1`  
`/thing/<page:int>` - List all things, paginated  
`/thing/<asset:suid>` - Get info about specific thing  
`/thing/<asset:suid>/edit` - Edit specific thing  
`/thing/asset/<asset:suid>` - Redirects to `/thing/asset/<asset:suid>/1`  
`/thing/asset/<asset:suid>/<page:int>` - List all things of asset type, paginated  
`/combo` - Get list of all combo types available  
`/combo/<combo:suid>` - Get info about specific combo  
`/combo/<combo:suid>/edit` - Edit combo type  
`/combo/<combo:suid>/new` - Create new thing of combo type  
`/combo/new` - Create new combo type  
`/group` - List all groups  
`/group/<combo:suid>` - Get info about specific group  
`/group/<combo:suid>/edit` - Edit specific group  
`/group/combo/<combo:suid>` - List all groups of combo type  

## License
[MIT License](https://opensource.org/licenses/MIT)
