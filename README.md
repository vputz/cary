Cary
----

Cary is a simple email gateway script intended for asynchronous tasks.
The name came from a job where I was working on grants (Cary... get it?)
and had a very restricted network, but wanted to build tools for assisting
me.  Since many websites and related technologies were blocked, but email
was usable, I decided that an offline email gateway was preferable,
and attempted to design one in a modular manner with several plugins
available.

In the base module, only the command "echo" is available, which simply echoes
the text of the email (and attachments) back to the user, for testing.
