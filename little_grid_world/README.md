## Little Grid World, Day 1 10/27/2023
got grid working, random color generator character faces 
space to paint, online networking with sockets, "camera"
system, shit ass memory system using json (change that later)
got up and running on heroku. took forever. Using poetry with 
heroku is not super fun 

## Little Grid World, Day 2 10/29/2023
grey area beyoond where you can go DONE
optimization - chunks DONE
make chunks user dependent DONE
grid stops at a certain point (100x100)- DONE
try to figure out why it slows down when you 
go to a low area on the map - DONE
tool for converting bitmap images into json memory - DONE 
- test performance on map full of pixels - DONE
was terrible, spent allmost all day trying to improve 
performance, less dom manipulation so less redrawing + drawing 
and culling videogame style + limit inputs on client side
+ cleaned up server code a little
add arrow key support - DONE
color picker
 - Just a color picker -DONE

TO DO 
usernames, with little minecreaft style tags (maybe they only show up on hover) 
usernames 
 - modal 
 - client memory
 - nametag 
 - who's here? like a list of people in the server
custom website name
 - DNS 
 - Favicon 
 connect json to S3 so we can have real data persistance
maybe create a git like system using delta compression for saving 
historical grid data 
make little animations, such as blinking
add messaging

11/3/2023
well this is depressing, I spent days dreaming up optimizations to try and make things faster, and guess waht
I made them slower if anything. what the fuck. this is with shit ass graphics too. how could it be slower????
well as winston (fat faggot) church hill once said: when you are going through hell, keep going. I shall. 
I am really not sure why this would be the case.

11/4/2023
I gave chat gpt my profiling results from the browser, here is its response:

Scripting (79 ms): This is the time spent executing JavaScript. It includes parsing JS, compilation, and the actual execution of scripts. In this summary, the time spent on scripting is relatively small, which suggests that JavaScript computation is likely not your performance bottleneck.

Rendering (8 ms): This is the time spent on the browser's rendering pipeline tasks, such as calculating layout (reflow) and updating the style (style recalculations) of elements on the page. Again, the time is quite low, indicating that style calculations and layout are not causing significant delays.

Painting (4 ms): This involves filling in pixels for the visual elements, including text, images, borders, shadows, etc. The low time here suggests that painting is not a performance issue.

System (118 ms): This is time spent by the browser in activities other than running your JavaScript, rendering, or painting, such as handling events or processing asynchronous operations. This could involve some garbage collection or other browser internals. This time is not very high, but it's worth noting if it increases significantly during more intensive operations.

Idle (17,606 ms): This is the time when the browser is not doing anything. A high idle time relative to the total time suggests that the browser is often waiting. This could mean that it's waiting for network responses or other resources, indicating that I/O or network latency could be a bottleneck.

Total (17,814 ms): The total time for all the recorded tasks to complete.

Interpretation:
The majority of the time, the browser is idle, which means that the issue causing slowness is likely not related to the processing power of the client's machine or the efficiency of your client-side code (at least, not the part that was profiled). Instead, it may be related to waiting for something, possibly network-related such as WebSocket messages, AJAX requests, or even waiting for the server to perform computations and send back responses.

Since you're using WebSockets, ensure that messages are being handled promptly and efficiently, both on the server and the client side.

I have a feeling I am just using websockets completely wrong, and truthfully, I am not even sure what a web socket is. I will spend most of my time trying to ammend that, for now I am going to work on another project that is more of a tutorial project by following along with the flask socketio docs. 

however many hours later and guess what. shits working... real well. it turned out to be three main problems and I was wayyyy overthinking shit
problem 1: I was sending too much data, every single time the player moved I sent the data for all the colors of the grid, when I actually just need to send that once when they first connect, then send just the color of the pixed they are moving off of when they move
problem 2: Input buffering. I needed to write a little loop that makes sure a given command to the server is completed before the next one can even register, with this in light I rewrote the movement stuff. 
problem 3: I was not using eventlets, I am not gonna question it but apparently this made a huge difference, whatever Im happy. 
problem 3.A: maybe switching to html5 canvas helped? honestly though it probably didnt change shit. Oh well! you live and learn. now the very best way to store the color data would be like a single hex pair 00 - FF


