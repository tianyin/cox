Cox
=================
A configuration navigation tool and library for a thousands of knobs.

### What's the problem? ###

*"How many configuration parameters ("knobs") do your system have?"*

0? Congrats! You can forget about Cox.

Usually, system users have to face a big bunch of configuration knobs they have no idea what to do with them. Here is some numbers from three mature software projects,

| Software      | Version  | # Parameters  |
| ------------- |:--------:| -------------:|
| Apache httpd  | 2.4.3    |    __587__    |
| MySQL         | 5.6      |    __461__    |
| Hadoop        | 2.2.0    |    __312__    |

Studies show that up to 48.5% of the configuration problems asked on Q&A forums and mailing lists are simply, 

    "Which knob(s) to set to achieve feature A or performance B?"

Don't blame your users, because it's really hard to find the correct knob from hundreds, especially the users are often not familiar with the system internals.

### What can Cox do? ###

The best solution to the "too many knobs" problem is to cleanup all the parameters your users do not need.

If you still have too many left or you don't want to touch the code, you can ask Cox for help.

As a navigation tool, Cox takes the users' query and returns a ranked list of knobs relevant to the queries.

Let me use a [real-world cases](http://serverfault.com/questions/490793/setting-up-mod-proxy-in-apache) as an example, where the user's question is:

    *"How do I configure the proxy to forward all requests?"*

She can type,:

    $cox "How do I configure the proxy to forward all requests"

which returns (only show the first 5):

    ['ProxyRequests', 'SSLProxyEngine', 'ProxyMaxForwards', 'ProxyPass', 'Location', ...]

Wooohooo, the knob desired by the user, ProxyRequests, is ranked #1. 





 









 

