User simulation package
======

Main purpose behind the package is to abstract the simulation of the user
actions in a way that many scripts can be executed simulating the user either
locally or remotely thru for example a vnc connection

In order to address some challenging things simulating the end user thru vnc
allows us to do interesting things, like for example privilege elevations,
logging on a different user and stuff that is much more complicated to do when
the user simulation is local, this is because the operating system for security
reasons will try to prevent certain things.

It does also spins and changes the more traditional way of writing a test
script, when the central figure is the 'user' it forces us to think in different
terms, like what the end user can do, and consequently what is more realistic
to test and perform.
 
There's no silver bullet and each approach has its pros and cons, use your own
judgment when is it worth using one or another depending on the circumstances

Some known limitations are that for example the VNC protocol does not know some
platform specific things, for example the windows key, the property key, etc

One key aspect to have in mind is that it does simulation, not emulation, it
means that it does not do low level message sending to windows or so, instead
it truly sets the mouse in a screen position, for keyboard simulates typing
instead of sending messages and so.
Consequently, you wont be able to click a button that is not visible, outside
the screen or covered by another window, while this is a bit more demanding
from the test it is also much more realistic and so the results of the tests.


PENDING:
Document the abstract class of a Keyboard, Mouse and Screen objects
