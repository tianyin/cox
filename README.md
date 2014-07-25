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

    "How do I configure the proxy to forward all requests?"

She can type,:

    $./cox "How do I configure the proxy to forward all requests"

which returns (only show the first 5):

    ['ProxyRequests', 'SSLProxyEngine', 'ProxyMaxForwards', 'ProxyPass', 'Location', ...]

Wooohooo, the knob desired by the user, ProxyRequests, is ranked #1. 

(This example is inside the *demo* directory)


### OK, I'm convinced. How can I use Cox to provide the navigation? ###

To use Cox as the developer, the only thing you have to do is breaking the user manual, parameter by parameter, into files. Each file should be named using the name of the parameter. Cox then builds indices based on these files. Breaking should be simple. We wrote the breakers for Apache httpd, MySQL, and Hadoop (checkout the dataset dir). The LOC of the breakers is only 62, 92, and 13 respectively.

There are some other optional information you can consider to tell Cox, so it can do a better job, including,

 - The popularity of each knob (from 0 to 1): a knob is less likely to be needed if it is rarely set by any user.
 - The knobs you don't want to return to users

Checkout the code to see the details.


### I really want to use it. Tell me more. ###

Cox mainly has two components, indexing and query processing.

*src* contains the source code of Cox

*lib* contains the external libs Cox needs; you need to add them into the classpath

*python-wrapper* allows your to use Cox using Python!

*benchmarks* evaluates the performance of Cox. It contains 90 real-world users' navigation issues collected from online Q&A forums and mailing lists: 39 for httpd, 25 for MySQL, and 26 for Hadoop. Currently, Cox is able to resolve 59 (28, 15, 16) of them (65.5%). We say Cox can resolve a issue if the target knob is among the top-5 returned parameters. 

You can run:
  
    python benchmarks/main.py

to see the detailed benchmarking results.


### Compile ###

You need [Apache Ant](http://ant.apache.org/) since Cox is written in Java. Apt-get or Yum it if you haven't installed it.

Once you have Ant ready, simply type:

    ant clean-build

to compile all the class files and cox.jar


### About ###

Drop us emails (tixu@ucsd.edu or athrunarthur@gmail.com) for anything you want to know.


