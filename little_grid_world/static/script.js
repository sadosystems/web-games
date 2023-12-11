document.addEventListener("DOMContentLoaded", function () {
    const socket = io.connect(location.origin);
    const gridCount = 104
    // init gloabals 
    let topPos = 0; 
    let leftPos = 0;
    let local_squares = []
    var local_players = {}
    // helper funcs (non handle)
    // make up a new player Id, if one isnt already in client memory  
    let playerId = localStorage.getItem('playerId');

    if (!playerId) {
        playerId = Math.random().toString(36).substr(2, 9);
        localStorage.setItem('playerId', playerId);
    }

    // Setup canvas stuff Setting the canvas width and height to occupy full window size
    const canvasDiv = document.getElementById('gameCanvasDiv');
    const canvas = document.getElementById('gameCanvas');
    const cordTracker = document.getElementById('cords');
    const mainCanvasRect = canvas.getBoundingClientRect();
    const ctx = canvas.getContext('2d');
    canvas.width = gridCount;
    canvas.height = gridCount;
    const gridSize = 35;
    // ctx.scale(0.06, 0.06); // this is a hack shit way, must change. 
    canvas.style.transformOrigin = 'top left';
    let scale = gridSize;
    canvas.style.transform = `scale(${scale})`;

    function drawSmiley(smiley_x, smiley_y, color, playerid) {
        let resMultiple = 2
        let face_scale = (1/resMultiple)
        let canvasSize = gridSize * resMultiple
        // create div for the canvases 
        let playerDiv = document.createElement('div');
        playerDiv.style.position = 'relative';
        playerDiv.style.left = (mainCanvasRect.left + (smiley_x*(gridSize))) + 'px';
        playerDiv.style.top = (mainCanvasRect.top + (smiley_y*(gridSize))) + 'px';
        playerDiv.style.transformOrigin = 'top left';

        canvasDiv.style.transformOrigin = 'top left';
        // text box 
        let textBox = document.createElement('input');
        textBox.type = 'text'; // Set type to text for text input

        textBox.value = local_players[playerid].username;
        if (!local_players[playerid].username){
            textBox.value = "";
        }
        textBox.size="10"
        textBox.style.textAlign = 'center';
        textBox.style.backgroundColor = 'rgba(8, 9, 20, 0.2)'; // Transparent black background
        textBox.style.color = 'white'; // White text
        textBox.style.border = 'none'; // No border
        textBox.style.padding = '0.5px'; // Some padding for text
        textBox.style.borderRadius = '5px'; // Rounded corners
        textBox.style.position = 'absolute'; // Position absolutely to float
        textBox.style.zIndex = '10'; // Ensure it's above other elements
        
        // Position the text box so that it floats above the playerDiv
        textBox.style.bottom = 'calc(100% + 10px)'; // Position at the bottom of playerDiv, then move it up by its own height
        textBox.style.left = 'calc(0% + 17px)'; // Center horizontally relative to playerDiv
        textBox.style.transform = 'translateX(-50%)'; // Adjust horizontal centering
        
        // Append the text box to playerDiv
        playerDiv.appendChild(textBox);
        // Create the new high-res canvas for face
        let faceCanvas = document.createElement('canvas');
        faceCanvas.width = canvasSize;
        faceCanvas.height = canvasSize; 
        faceCanvas.style.position = 'absolute';
        // faceCanvas.style.left = (mainCanvasRect.left + (smiley_x*(gridSize))) + 'px';
        // faceCanvas.style.top = (mainCanvasRect.top + (smiley_y*(gridSize))) + 'px';
        faceCanvas.style.transformOrigin = 'top left';
        faceCanvas.style.transform = `scale(${face_scale})`;
        // create new low res canvas for border
        let borderCanvas = document.createElement('canvas');
        borderCanvas.width = canvasSize; // Width of the X canvas
        borderCanvas.height = canvasSize; // Height of the X canvas
        borderCanvas.style.position = 'absolute';
        // borderCanvas.style.left = (mainCanvasRect.left + (smiley_x*(gridSize))) + 'px'// Position X canvas at the top-left corner of the main canvas
        // borderCanvas.style.top = (mainCanvasRect.top + (smiley_y*(gridSize))) + 'px';
        borderCanvas.style.mixBlendMode = 'color-burn';
        borderCanvas.style.transformOrigin = 'top left';
        let border_scale = (1/resMultiple)
        borderCanvas.style.transform = `scale(${border_scale})`;

        // drawaing border
        const centerX = faceCanvas.width / 2;
        const centerY = faceCanvas.height / 2;
        let borderctx = borderCanvas.getContext('2d');
        borderctx.fillStyle = "#c8cbe6"
        borderctx.fillRect(0, 0, canvasSize, canvasSize);
        borderctx.fillStyle = "#FFFFFF"
        borderctx.fillRect(5, 5, canvasSize-10, canvasSize-10);
        // drawing smiley 
        // smiley constants
        let smileyctx = faceCanvas.getContext('2d');
        const eyeRadius = gridSize / 8;
        const interEye = 18
        const eyeHeight = 5
        
        smileyctx.fillStyle = color;
        smileyctx.beginPath();
        smileyctx.arc(centerX-interEye, centerY+eyeHeight, eyeRadius, 0, Math.PI * 2);
        smileyctx.fill();
        
        // Right eye
        smileyctx.beginPath();
        smileyctx.arc(centerX+interEye, centerY+eyeHeight, eyeRadius, 0, Math.PI * 2);
        smileyctx.fill();

        // Draw mouth
        const mouthWidth = 35;
        const mouthY = centerY +17; // Y-position of the mouth; adjust as needed
        const controlPointY = centerY + 25; // Y-position of the control point; adjust for curvature

        smileyctx.beginPath();
        // Start point of the mouth on the left
        smileyctx.moveTo(centerX - mouthWidth / 2, mouthY);
        // Quadratic curve to right
        smileyctx.quadraticCurveTo(centerX, controlPointY, centerX + mouthWidth / 2, mouthY);        
        smileyctx.strokeStyle = color;
        smileyctx.lineWidth = 4; // Setting a thicker stroke
        smileyctx.stroke();

        playerDiv.appendChild(faceCanvas); 
        playerDiv.appendChild(borderCanvas); 
        canvasDiv.appendChild(playerDiv); 

        // canvasDiv.appendChild(faceCanvas); 
        // canvasDiv.appendChild(borderCanvas); 
        return [playerDiv, function(newUsername) {
            textBox.value = newUsername;
        }];
    }
    
    function drawPlayers(players){
        for (const player in players) {
            let x = players[player].x
            let y = players[player].y
            let color = players[player].color
            let face_color = players[player].face_color
            updateGrid(x,y,color)
            let thisPlayerDiv = local_players[player].playerDiv
            if (thisPlayerDiv) {
                thisPlayerDiv.style.left = (mainCanvasRect.left + (x*(gridSize))) + 'px';
                thisPlayerDiv.style.top = (mainCanvasRect.top + (y*(gridSize))) + 'px';
            }
        }  
    }

    function hexToRGBA(hexColor) {
        var rgba = [];
        hexColor = hexColor.replace(/^#/, '');
        rgba.push(parseInt(hexColor.substring(0, 2), 16)); // Red
        rgba.push(parseInt(hexColor.substring(2, 4), 16)); // Green
        rgba.push(parseInt(hexColor.substring(4, 6), 16)); // Blue
        rgba.push(255); // Alpha (fully opaque)
        return rgba;
    }

    function initFaces(players){
        for (const player in players) {
            // console.log(players[player])
            let x = players[player].x
            let y = players[player].y
            let face_color = players[player].face_color
        
            let [playerDiv, update_name] = drawSmiley(x,y,face_color, player);
            local_players[player].playerDiv = playerDiv;
            local_players[player].update_name = update_name;
        }  

        for (const player in players) {
            let thisPlayerDiv = local_players[player]
        }
    }

           // if (local_players[player].playerDiv.parentNode) {
            //     // Remove the playerDiv from the DOM
            //     console.log("parentNode found")
            // }
    function centerGridSquareAt(x, y) {
        const viewportWidth = document.documentElement.clientWidth;
        const viewportHeight = document.documentElement.clientHeight;
        
        const squareTopLeftX = x * gridSize;
        const squareTopLeftY = y * gridSize;
    
        const squareCenterX = squareTopLeftX + gridSize / 2;
        const squareCenterY = squareTopLeftY + gridSize / 2;
    
        const offsetX = viewportWidth / 2 - squareTopLeftX;
        const offsetY = viewportHeight / 2 - squareTopLeftY;
    
        canvasDiv.style.position = 'absolute'; // Ensure the div is positioned absolutely
        canvasDiv.style.transformOrigin = 'top left';
        canvasDiv.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
    }

    function updateGrid(x, y, color){
        var rgbaColor = hexToRGBA(color)
        var pixelData = new Uint8ClampedArray(rgbaColor);
        var imageData = new ImageData(pixelData, 1, 1);
        ctx.putImageData(imageData, x, y);
        }
   
    function drawPixels(squares){
    for (let i = 0; i < gridCount; i++) {
        for (let j = 0; j < gridCount; j++) {
            let index = i + j* gridCount;
            let color = squares[index];
            updateGrid(i, j, color)
            }
        }
    }

    // Example scale values; replace these with your actual scale values
    var scaleX = 1.5; // Horizontal scale
    var scaleY = 1.5; // Vertical scale

    // Function to get the mouse position adjusted for scale
    function getMousePos(canvas, evt) {
        var rect = canvas.getBoundingClientRect();
        return {
            x: (evt.clientX - rect.left) / scaleX, // Adjust X position for scale
            y: (evt.clientY - rect.top) / scaleY   // Adjust Y position for scale
        };
    }

    // Event listener for mousemove
    canvas.addEventListener('mousemove', function(evt) {
        var mousePos = getMousePos(canvas, evt);
        var x = Math.floor((mousePos.x)/23.32692307692307692308);
        // var x = Math.round(mousePos.x);
        var y = Math.floor((mousePos.y)/23.32692307692307692308);
        var pixel = ctx.getImageData(x, y, 1, 1).data;
        var new_cords = `${x},${y}:`; // Use backticks (`` ` ``) instead of single quotes

        if (!cordTracker.textContent.includes(new_cords)) {
            console.log('Mouse position: ' + x + ',' + y);
            cordTracker.textContent = `${x},${y}: `; 
            socket.emit('fetch_blame', { x: x, y: y });
        }
    });

    socket.on('return_blame', function(data) {
        cordTracker.textContent += data; 
    });

    window.addEventListener('resize', function() {
        canvas.width = gridCount;
        canvas.height = gridCount;
        drawPixels(local_squares)
        // drawPixels(local_squares)
        if (Object.keys(local_players).length) {
            drawPlayers(local_players);
        }

    });

    function createOneTimeInitFaces() {
        let called = false;
    
        return function() {
            if (called) {
                return;
            }
    
            called = true;
            initFaces(local_players);
        };
    }
    
    // Usage
    const oneTimeInitFaces = createOneTimeInitFaces();

    socket.on('paint_grid', function(data) {
        // only do this once!!
        // console.log('paint grid')
        local_squares = data.squares
        local_players = data.players
        drawPixels(data.squares)
        let xpos = data.players[playerId].x
        let ypos = data.players[playerId].y
        drawPlayers(local_players);
        centerGridSquareAt(xpos, ypos);
        document.getElementById('colorPicker').value = data.players[playerId].color;
    });

    socket.on('ask_for_player_id', function(data) {
        socket.emit('after_connect', playerId);
    });

    socket.on('update_local_squares', function(data) {
        index = data.x + data.y * gridCount
        local_squares[index] = data.color;
    });

    function updateLocalPlayers(newData) {
        for (const playerId in newData) {
          if (newData.hasOwnProperty(playerId)) {
            local_players[playerId] = {
              ...local_players[playerId],
              ...newData[playerId]
            };
          }
        }
      }
      
    socket.on('draw_players', function(data) {
        // Overdrawing rectangle player was last on
        console.log(local_players)
        let x = data.x
        let y = data.y
        let index = x + y * gridCount
        let color = data.previous_color;
        updateGrid(x, y, color)
        // Actually drawing players
        updateLocalPlayers(data.players);
        drawPlayers(local_players)
        centerGridSquareAt(data.players[playerId].x, data.players[playerId].y);
        oneTimeInitFaces()

    });

    // ------------------- PLAYER MOVEMENT STUFF -----------------------

    const moveInterval = 20; // Time in milliseconds
    let lastMoveTime = 0;
    let direction = null;
    let waitingForMoveCompletion = false;

    function setDirection(newDirection) {
        direction = newDirection;
        if (canMove() && !waitingForMoveCompletion) {
            waitingForMoveCompletion = true;
            socket.emit('player_move', { player_id: playerId, direction: direction }, () => {
                // Acknowledgment callback
                waitingForMoveCompletion = false;
                if (direction) {
                    // If the key is still pressed, immediately try another move
                    tryMove();
                }
            });
        }
    }

    function tryMove() {
        if (canMove() && direction && !waitingForMoveCompletion) {
            waitingForMoveCompletion = true;
            socket.emit('player_move', { player_id: playerId, direction: direction }, () => {
                waitingForMoveCompletion = false;
            });
        }
    }

    function canMove() {
        const currentTime = new Date().getTime();
        if (currentTime - lastMoveTime >= moveInterval) {
            lastMoveTime = currentTime;
            return true;
        }
        return false;
    }

    colorPicker.addEventListener('input', function(event) {
        var selectedColor = event.target.value; // Getting the selected color
        socket.emit('color_change', { player_id: playerId, color: selectedColor }); // Emitting the color_change event
    });
    
    socket.on('update_positions', drawPlayers);

    // username stuff
    function validateInput() {
        var inputValue = usernameBox.value;
        var bannedWords = ['God', 'god', 'Alex', 'alex', 'theNword'];

        // Replace 'disallowedValue' with the value you want to disallow
        if (bannedWords.includes(inputValue)) {
            // alert('This input is not allowed.');
            usernameDiv.classList.add('flash-red');
            usernameBox.value = ''; // Clear the input box
            local_players[playerId].update_name('')
            socket.emit('name_change', { player_id: playerId, username: '' });
            setTimeout(function() {
                usernameDiv.classList.remove('flash-red');
            }, 3000); 
            return false; // Indicate that the validation failed
        }
        return true; // Indicate that the validation passed
    }

    var usernameDiv = document.getElementById('username');
    var usernameBox = document.getElementById('username_box');
    usernameBox.maxLength = 15;
    usernameBox.addEventListener('input', function(event) {
        if (validateInput()) {
            usernameDiv.classList.remove('flash-red');
            var username = event.target.value; 
            console.log(local_players[playerId])
            local_players[playerId].update_name(username)
            socket.emit('name_change', { player_id: playerId, username: username });
        }
    });
    

    window.addEventListener('keydown', function(event) {
        if (event.repeat) { return; }
        let newDirection = null;
        switch (event.code) {
            case 'KeyW': case 'ArrowUp': newDirection = 'w'; break;
            case 'KeyA': case 'ArrowLeft': newDirection = 'a'; break;
            case 'KeyS': case 'ArrowDown': newDirection = 's'; break;
            case 'KeyD': case 'ArrowRight': newDirection = 'd'; break;
        }
        if (event.code === 'Space') {
            socket.emit('color_square', { player_id: playerId });
        }
        if (newDirection) {
            setDirection(newDirection);
        }
    });

    window.addEventListener('keyup', function(event) {
        // If the key released matches the current direction, stop moving
        let releasedDirection = null;
        switch (event.code) {
            case 'KeyW': case 'ArrowUp': releasedDirection = 'w'; break;
            case 'KeyA': case 'ArrowLeft': releasedDirection = 'a'; break;
            case 'KeyS': case 'ArrowDown': releasedDirection = 's'; break;
            case 'KeyD': case 'ArrowRight': releasedDirection = 'd'; break;
        }
        if (releasedDirection && direction === releasedDirection) {
            direction = null;
        }
    });
    // basically polling... smh
    
    setInterval(tryMove, moveInterval);
    // setTimeout(function() {
    //     initFaces(local_players);
    // }, 5000);
});
