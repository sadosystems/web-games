// this is the first js I have ever written I am aware this is an ugly mess
document.addEventListener("DOMContentLoaded", function () {
  const socket = io.connect(location.origin);
  const gridCount = 20;
  let local_squares = [];
  var local_players = {};
  let playerId = localStorage.getItem("playerId");

  if (!playerId) {
    playerId = Math.random().toString(36).substr(2, 9);
    localStorage.setItem("playerId", playerId);
  }
  const trace_circle = document.getElementById("trace");
  const void_circle = document.getElementById("void");
  const input_circle = document.getElementById("input");

  // Setup canvas stuff Setting the canvas width and height to occupy full window size
  const canvasDiv = document.getElementById("gameCanvasDiv");
  const canvas = document.getElementById("gameCanvas");

  const cordTracker = document.getElementById("cords");
  const mainCanvasRect = canvas.getBoundingClientRect();
  const ctx = canvas.getContext("2d");
  canvas.width = gridCount;
  canvas.height = gridCount;
  const gridSize = 35;
  canvas.style.transformOrigin = "top left";
  let scale = gridSize;
  canvas.style.transform = `scale(${scale})`;


  function drawPlayers(players) {
    for (const player in players) {
      let x = players[player].x;
      let y = players[player].y;
      let color = players[player].color;

    }
  }

  function hexToRGBA(hexColor) {
    var rgba = [];
    hexColor = hexColor.replace(/^#/, "");
    rgba.push(parseInt(hexColor.substring(0, 2), 16)); // Red
    rgba.push(parseInt(hexColor.substring(2, 4), 16)); // Green
    rgba.push(parseInt(hexColor.substring(4, 6), 16)); // Blue
    rgba.push(255); // Alpha
    return rgba;
  }

  function initFaces(players) {
    for (const player in players) {
      let x = players[player].x;
      let y = players[player].y;
      let face_color = players[player].face_color;

      // let [playerDiv, update_name] = drawSmiley(x, y, face_color, player);
      local_players[player].playerDiv = playerDiv;
      local_players[player].update_name = update_name;
    }

    for (const player in players) {
      let thisPlayerDiv = local_players[player];
    }
  }

  function centerGridSquareAt(x, y) {
    const viewportWidth = document.documentElement.clientWidth;
    const viewportHeight = document.documentElement.clientHeight;

    const squareTopLeftX = x * gridSize;
    const squareTopLeftY = y * gridSize;

    const squareCenterX = squareTopLeftX + gridSize / 2;
    const squareCenterY = squareTopLeftY + gridSize / 2;

    const offsetX = viewportWidth / 2 - squareTopLeftX;
    const offsetY = viewportHeight / 2 - squareTopLeftY;

    canvasDiv.style.position = "absolute";
    canvasDiv.style.transformOrigin = "top left";
    canvasDiv.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
  }

  function updateGrid(x, y, color_id) {
    let color = idToColor(color_id);
    var rgbaColor = hexToRGBA(color);
    var pixelData = new Uint8ClampedArray(rgbaColor);
    var imageData = new ImageData(pixelData, 1, 1);
    ctx.putImageData(imageData, x, y);
  }
  function lighten_color(x, y) {
    let imageData = ctx.getImageData(x, y, 1, 1);
    let data = imageData.data;
    let increaseFactor = 10;
    data[0] = Math.min(255, data[0] + increaseFactor); // Red
    data[1] = Math.min(255, data[1] + increaseFactor); // Green
    data[2] = Math.min(255, data[2] + increaseFactor); // Blue
    ctx.putImageData(imageData, x, y);
  }
  const idToColorTable = {
    0x0: "#09192e", // void
    0x1: "#3b3405", // trace
    0x2: "#a6951f", // trace
    0xA: "#cfc580",  // logic high
    0xF: "#5f6a78"
  };

  function idToColor(id) {
      return idToColorTable[id] || "#000000"; // Default to "#000000" if id is not found
  }

  function drawPixels(squares) {
    for (let i = 0; i < gridCount; i++) {
      for (let j = 0; j < gridCount; j++) {
        let index = i + j * gridCount;
        let color = squares[index];
        updateGrid(i, j, color);
      }
    }
  }

  var scaleX = 1.5;
  var scaleY = 1.5;

  function getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect();
    return {
      x: (evt.clientX - rect.left) / scaleX,
      y: (evt.clientY - rect.top) / scaleY, 
    };
  }
  var globalX = 0;
  var globalY = 0;

  canvas.addEventListener("mousemove", function (evt) {
    var mousePos = getMousePos(canvas, evt);
    var x = Math.floor(mousePos.x / 23.32692307692307692308);
    var y = Math.floor(mousePos.y / 23.32692307692307692308);
    var pixel = ctx.getImageData(x, y, 1, 1).data;
    globalX = x;
    globalY = y;

    var new_cords = `${x},${y}:`; 
    lighten_color(x, y)

    if (!cordTracker.textContent.includes(new_cords)) {
      // console.log("Mouse position: " + x + "," + y);
      cordTracker.textContent = `${x},${y}: `;
      // socket.emit("fetch_blame", { x: x, y: y });
    }
  });
var picked_color = 1
  canvasDiv.addEventListener("click", function(evt) {
    console.log("Mouse click position: " + globalX + "," + globalY);
    socket.emit("color_square_click", { color: picked_color, x:globalX, y:globalY});
});

void_circle.addEventListener("click", function(evt) {
  picked_color = 0
});
trace_circle.addEventListener("click", function(evt) {
  picked_color = 0
});
input_circle.addEventListener("click", function(evt) {
  picked_color = 10
});

  socket.on("return_blame", function (data) {
    cordTracker.textContent += data;
  });

  window.addEventListener("resize", function () {
    canvas.width = gridCount;
    canvas.height = gridCount;
    drawPixels(local_squares);
    if (Object.keys(local_players).length) {
      drawPlayers(local_players);
    }
  });

  function createOneTimeInitFaces() {
    let called = false;

    return function () {
      if (called) {
        return;
      }

      called = true;
      initFaces(local_players);
    };
  }

  const oneTimeInitFaces = createOneTimeInitFaces();

  socket.on("paint_grid", function (data) {
    local_squares = data.squares;
    local_players = data.players;
    drawPixels(data.squares);
    let xpos = data.players[playerId].x;
    let ypos = data.players[playerId].y;
    drawPlayers(local_players);
    centerGridSquareAt(xpos, ypos);
  });

  socket.on("ask_for_player_id", function (data) {
    socket.emit("after_connect", playerId);
  });

  socket.on("update_local_squares", function (data) {
    index = data.x + data.y * gridCount;
    local_squares[index] = data.color;
  });

  function updateLocalPlayers(newData) {
    for (const playerId in newData) {
      if (newData.hasOwnProperty(playerId)) {
        local_players[playerId] = {
          ...local_players[playerId],
          ...newData[playerId],
        };
      }
    }
  }

  socket.on("draw_players", function (data) {
    // Overdrawing rectangle player was last on
    // console.log(local_players);
    let x = data.x;
    let y = data.y;
    let index = x + y * gridCount;
    let color = data.previous_color;
    // updateGrid(x, y, color);
    // Actually drawing players
    updateLocalPlayers(data.players);
    drawPlayers(local_players);
    centerGridSquareAt(data.players[playerId].x, data.players[playerId].y);
    // oneTimeInitFaces();
  });

  // ------------------- PLAYER MOVEMENT STUFF -----------------------

  const moveInterval = 20;
  let lastMoveTime = 0;
  let direction = null;
  let waitingForMoveCompletion = false;

  function setDirection(newDirection) {
    direction = newDirection;
    if (canMove() && !waitingForMoveCompletion) {
      waitingForMoveCompletion = true;
      socket.emit(
        "player_move",
        { player_id: playerId, direction: direction },
        () => {
          // Acknowledgment callback
          waitingForMoveCompletion = false;
          if (direction) {
            // If the key is still pressed, immediately try another move
            tryMove();
          }
        }
      );
    }
  }

  function tryMove() {
    if (canMove() && direction && !waitingForMoveCompletion) {
      waitingForMoveCompletion = true;
      socket.emit(
        "player_move",
        { player_id: playerId, direction: direction },
        () => {
          waitingForMoveCompletion = false;
        }
      );
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


  socket.on("update_positions", drawPlayers);

  // username stuff


  window.addEventListener("keydown", function (event) {
    if (event.repeat) {
      return;
    }
    let newDirection = null;
    switch (event.code) {
      case "KeyW":
      case "ArrowUp":
        newDirection = "w";
        break;
      case "KeyA":
      case "ArrowLeft":
        newDirection = "a";
        break;
      case "KeyS":
      case "ArrowDown":
        newDirection = "s";
        break;
      case "KeyD":
      case "ArrowRight":
        newDirection = "d";
        break;
    }
    if (event.code === "Space") {
      socket.emit("color_square_click", { color: 1, x:globalX, y:globalY});
      }
    if (newDirection) {
      setDirection(newDirection);
    }
  });

  window.addEventListener("keyup", function (event) {
    // If the key released matches the current direction, stop moving
    let releasedDirection = null;
    switch (event.code) {
      case "KeyW":
      case "ArrowUp":
        releasedDirection = "w";
        break;
      case "KeyA":
      case "ArrowLeft":
        releasedDirection = "a";
        break;
      case "KeyS":
      case "ArrowDown":
        releasedDirection = "s";
        break;
      case "KeyD":
      case "ArrowRight":
        releasedDirection = "d";
        break;
    }
    if (releasedDirection && direction === releasedDirection) {
      direction = null;
    }
  });
  // basically polling... smh
  setInterval(tryMove, moveInterval);
});
