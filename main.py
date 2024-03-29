import pygame as pg
from game import game,degrees,pl1Keys,pl2Keys,get_key
from settings import white,snakeColors,maxInitialSpeed,scoreboardMargin

def main():
    # Creates Snake #1
    headPart = game.createSnakePart('head',0,game.player1Color,False,False,True)
    game.createSnakePart('tail',0,game.player1Color, (headPart.pos[0]-1,headPart.pos[1]))
    for snakePart in game.snakeParts: game.moveSnakePart(snakePart,snakePart.pos)

    # Creates Snake #2
    if game.multiplayer:
        headPart = game.createSnakePart('head',1,game.player2Color,False,False,True)
        game.createSnakePart('tail',1,game.player2Color,(headPart.pos[0]-1,headPart.pos[1]))
        for snakePart in game.snakeParts: game.moveSnakePart(snakePart,snakePart.pos)

    # Adding first food
    for i in range(game.foodCount):
        game.createFood(False)
    # Adding first poisonous food
    for i in range(game.poisonousFoodCount):
        game.createFood(True)
        
    game.getMovementPeriod()
    # Active action loop
    game.active = True
    while game.active:
        # Updates game state
        game.onUpdate()
        # Snake speed increment
        if game.speedIncAfterEat and (game.snake1PartAddedFired or game.snake2PartAddedFired):
            game.movementPeriod = game.movementPeriod * .95
        # Add score text
        game.getPlayersScore()
        score1Text = game.gameOverFont.render(f'{"P1 " if game.multiplayer else ""}SCORE: {(game.player1Score-1)*10}', True, white)
        game.screen.blit(score1Text, game.score1Pos)
        if game.multiplayer:
            score2Text = game.gameOverFont.render(f'P2 SCORE: {(game.player2Score-1)*10}', True, game.player2Color)
            game.screen.blit(score2Text, (game.score2Pos[0]-score2Text.get_width(), game.score2Pos[1]))
        # Events
        headParts = [x for x in game.snakeParts if x.type == 'head']
        if game.isQuit(False): quit()

        # Dont move unsless movement button's been pressed
        if (game.isKey(pg.K_RIGHT) or game.isKey(pg.K_UP) or game.isKey(pg.K_LEFT) or game.isKey(pg.K_DOWN)) and headParts[0].velocity.length() == 0: 
            pg.time.set_timer(game.moveEvent, game.movementPeriod)
            game.setBaseVelocity()
        if game.multiplayer and (game.isKey(pg.K_d) or game.isKey(pg.K_w) or game.isKey(pg.K_a) or game.isKey(pg.K_s)) and headParts[0].velocity.length() == 0:
            pg.time.set_timer(game.moveEvent, int(game.movementPeriod))
            game.setBaseVelocity()
        # Changes snakes direction
        if not game.player1ChangedDir:
            for i,key in enumerate(pl1Keys):
                if game.isKey(key):
                    headParts[0].changeDirToAnAngle(degrees[i])
                    headParts[0].changedDirection = True
                    game.player1ChangedDir = True
        if not game.player1ChangedDir and game.multiplayer:
            for i,key in enumerate(pl2Keys):
                if game.isKey(key):
                    headParts[1].changeDirToAnAngle(degrees[i])
                    headParts[1].changedDirection = True
                    game.player2ChangedDir = True
        # Snakes' movement
        if not game.isSnakeDead():
            if game.moveEventFired:
                for headPart in headParts:
                    headPart.getRelatedSnakeParts()
                    for i, part in enumerate(headPart.relatedSnakeParts):
                        part.prevPos, part.prevVelocity = (part.pos[0],part.pos[1]), pg.Vector2((part.velocity.x,part.velocity.y))
                        game.moveSnakePart(part,part.pos,part.velocity)
                        if part.type != 'head': part.velocity = pg.Vector2(headPart.relatedSnakeParts[i-1].prevVelocity)
                        if part.type == 'head':
                            part.changedDirection = False
                            if part.snakeIndex == 0:
                                game.player1ChangedDir = False
                            if part.snakeIndex == 1:
                                game.player2ChangedDir = False
        # Snake sprite turning
            for headPart in headParts:
                headPart.getRelatedSnakeParts()
                for i, part in enumerate(headPart.relatedSnakeParts):
                    if game.moveEventFired:
                        if part.type == 'head' and part.changedDirection == True: 
                            game.screen.blit(part.sprite, (part.rect.x, part.rect.y))
                            continue
                        part.getAngle().rotateSprite()
                    elif ((game.snake1PartAddedFired if headPart.snakeIndex == 0 else game.snake2PartAddedFired) and part.type != 'head'):
                        part.getAngle().rotateSprite()
                    game.screen.blit(part.sprite, (part.rect.x, part.rect.y))
        if game.moveEventFired:
            for headPart in headParts:
                for i, part in enumerate(headPart.relatedSnakeParts):
                    # Check food collision
                    for food in game.foods:
                        if game.checkRectalCollision(part.pos, food.pos):
                            headPart.relatedSnakeParts = [x for x in game.snakeParts if x.snakeIndex == part.snakeIndex]
                            if food.type == 'food':
                                lastSnakePart = headPart.relatedSnakeParts[-1]
                                lastSnakePart.type = 'body'
                                game.foods.remove(food)
                                poisonousFood = game.getRandomFood(True)
                                if game.poisonousFoodRespawn:
                                    game.foods.remove(poisonousFood)
                                game.createSnakePart('tail',part.snakeIndex,part.color,lastSnakePart.prevPos,pg.Vector2(lastSnakePart.prevVelocity))
                                if  part.snakeIndex == 0: event = pg.event.Event(game.snake1PartAdded)
                                else: event = pg.event.Event(game.snake2PartAdded)
                                pg.event.post(event)
                                game.createFood(False)
                                if game.poisonousFoodRespawn:
                                    game.createFood(True)
                            if food.type == 'poison':
                                lastSnakePart = headPart.relatedSnakeParts[-1]
                                game.foods.remove(food)
                                if len(headPart.relatedSnakeParts) > 2:
                                    if lastSnakePart in game.snakeParts:
                                        game.snakeParts.remove(lastSnakePart)
                                    if lastSnakePart in part.relatedSnakeParts:
                                        part.relatedSnakeParts.remove(lastSnakePart)
                                    lastPart = headPart.relatedSnakeParts[-1]
                                    lastPart.type = 'tail'
                                    lastPart.getAngle().rotateSprite()
                                game.createFood(True)
                    # Check snake collision
                    if game.moveEventFired:
                        for i, part in enumerate(headPart.relatedSnakeParts):
                            # Passes if it is a head part
                            if part.type == 'head': continue
                            if game.availablePositions.count(headPart.pos) > 1:
                                part.alive = False
                            if game.checkRectalCollision(headPart.pos, part.pos):
                                part.alive = False
                        for part in game.snakeParts:
                            if headPart.snakeIndex != part.snakeIndex and game.checkRectalCollision(headPart.pos, part.pos):
                                headPart.alive, part.alive = False, False                      
            
        # Game over condition   
        if game.isSnakeDead():
            game.snakeParts.clear()
            game.foods.clear()
            game.getMovementPeriod()
            gameOver()
            break
        if game.isKey(pg.K_ESCAPE):
            game.snakeParts.clear()
            game.foods.clear()
            game.getMovementPeriod()
            break

        # Draws other elements
        game.screen.blit(game.topWallSprite,game.topBorder)
        game.screen.blit(game.bottomWallSprite,game.bottomBorder)
        game.screen.blit(game.leftWallSprite,game.leftBorder)
        game.screen.blit(game.rightWallSprite,game.rightBorder)
        rects = game.playfield.rects
        for food in game.foods: game.screen.blit(food.sprite, (food.rect.x, food.rect.y))

        # Event firing
        if game.moveEventFired: game.moveEventFired = False
        if game.isEvent(game.moveEvent): game.moveEventFired = True
        if game.snake1PartAddedFired: game.snake1PartAddedFired = False
        if game.isEvent(game.snake1PartAdded): game.snake1PartAddedFired = True
        if game.snake2PartAddedFired: game.snake2PartAddedFired = False
        if game.isEvent(game.snake2PartAdded): game.snake2PartAddedFired = True
        game.update()

# Game restart/quit screen
def gameOver():
    while True:
        game.onUpdate().setBackground()
        gameOverText = game.createMenuItem(f'GAME OVER | {("SCORE: "+str((game.player1Score-1)*10)) if not game.multiplayer else ("P1 SCORE: "+str((game.player1Score-1)*10)+" | P2 SCORE: "+str((game.player2Score-1)*10))}', white)
        escapeText = game.createMenuItem('PRESS ESC TO RETURN TO MAIN MENU', white)
        scoreboardSuggestText = game.createMenuItem('PRESS ANY KEY TO SAVE YOUR SCORE', white)
        menuItems = [gameOverText,escapeText]
        if(game.player1Score > 1 or game.player2Score > 1):
            menuItems.append(scoreboardSuggestText)
            if game.isKey(pg.K_ESCAPE):
                break
            if game.isAnyKey():
                nameField()
                break
        else:
            if game.isAnyKey():
                break
        game.showMenuItems(menuItems, False)
        if game.isQuit(False): quit()
        game.update()

def gameMenu():
    game.menuPointingTo = 0
    while True:
        game.onUpdate().setBackground()
        menuItems = []
        startBtn = game.createMenuItem('START')
        settingsBtn = game.createMenuItem('SETTINGS')
        scoreboardBtn = game.createMenuItem('SCOREBOARD')
        exitBtn = game.createMenuItem('EXIT')
        menuItems.extend([startBtn,settingsBtn,scoreboardBtn,exitBtn])
        game.showMenuItems(menuItems)
        if game.isKey(pg.K_UP):
            if game.menuPointingTo == 0: game.menuPointingTo = len(menuItems)-1
            else: game.menuPointingTo -= 1
        if game.isKey(pg.K_DOWN):
            if game.menuPointingTo == len(menuItems)-1: game.menuPointingTo = 0
            else: game.menuPointingTo += 1
        if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(startBtn): break
        if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(settingsBtn): 
            settingsMenu()
            game.menuPointingTo = 0
        if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(scoreboardBtn):
            scoreboard()
            game.menuPointingTo = 0
        if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(exitBtn): exit()
        game.update()

def scoreboard():
    scoreboardColumns = []
    singleplayerScoreboard = []
    multiplayerScoreboard = []
    singleplayerScoreboard.append(game.scoreboardFont.render('SINGLE PLAYER', True, white))
    records = []
    for id in game.singleplayerHighscores:
        record = game.singleplayerHighscores[id]
        records.append(record)
    records = sorted(records, key=lambda d: d['score'],reverse=True)
    singleplayerRecordTexts = [] 
    for rec in records:
        nickname = rec['nickname']
        score = rec['score']
        singleplayerRecordTexts.append(game.scoreboardFont.render(f'{nickname}: {score}', True, white))
    if len(singleplayerRecordTexts) > 0: singleplayerScoreboard.extend(singleplayerRecordTexts)
    multiplayerScoreboard.append(game.scoreboardFont.render('MULTIPLAYER', True, white))
    records = []
    for id in game.multiplayerHighscores:
        record = game.multiplayerHighscores[id]
        records.append(record)
    records = sorted(records, key=lambda d: d['score']+d['score_'],reverse=True)
    multiplayerRecordTexts = []
    for record in records:
        nickname = record['nickname']
        score = record['score']
        nickname_ = record['nickname_']
        score_ = record['score_']
        multiplayerRecordTexts.append(game.scoreboardFont.render(f'{nickname}: {score} {nickname_}: {score_}', True, white))
    if len(multiplayerRecordTexts) > 0: multiplayerScoreboard.extend(multiplayerRecordTexts)
    scoreboardColumns.extend([singleplayerScoreboard, multiplayerScoreboard])
    colCount = len(scoreboardColumns)
    while True: 
        game.onUpdate().setBackground()
        for i,c in enumerate(scoreboardColumns):
            textHeight = c[0].get_height()
            blockHeight = textHeight * len(c)
            for ind,t in enumerate(c):
                game.screen.blit(t, (game.SCREEN_WIDTH/(colCount*2)*(1+i*2)-t.get_width()/2, game.SCREEN_HEIGHT/2-t.get_height()-blockHeight/2+(textHeight+scoreboardMargin)*ind))
        if game.isKey(pg.K_ESCAPE):
            break
        if game.isQuit(False): quit()
        game.update()

def settingsMenu():
    game.menuPointingTo = 0
    while True:
        game.onUpdate().setBackground()
        menuItems = []
        wallMode = game.createMenuItem(f'WALL MODE: {"PORTAL" if game.portalWalls else "REGULAR"}')
        multiplayerOn = game.createMenuItem(f'MODE: {"1 PLAYER" if not game.multiplayer else "2 PLAEYRS"}')
        colorPlayer1Btn = game.createMenuItem(f'PLAYER 1 COLOR: {get_key(game.player1Color, snakeColors).upper()}')
        if game.multiplayer:
            if(game.player1Color == game.player2Color): game.getPlayerNextColor(1)
            colorPlayer2Btn = game.createMenuItem(f'PLAYER 2 COLOR: {get_key(game.player2Color, snakeColors).upper()}')
        speedIncAfterEatBtn = game.createMenuItem(f'SPEED INCREASE AFTER EATING: {"ON" if game.speedIncAfterEat else "OFF"}')
        initialSpeedBtn = game.createMenuItem(f'INITIAL SPEED: {game.initialSpeed}')
        foodCountBtn = game.createMenuItem(f'FOOD COUNT: {game.foodCount}')
        poisonousFoodCountBtn = game.createMenuItem(f'POISONOUS FOOD COUNT: {game.poisonousFoodCount}')
        poisonousFoodRespawnBtn = game.createMenuItem(f'POISONOUS FOOD RESPAWN: {"ON" if game.poisonousFoodRespawn else "OFF"}')
        backBtn = game.createMenuItem('BACK')
        menuItems.extend([wallMode, multiplayerOn,colorPlayer1Btn])
        if game.multiplayer:
            menuItems.append(colorPlayer2Btn)
        menuItems.extend([speedIncAfterEatBtn,foodCountBtn,poisonousFoodCountBtn,initialSpeedBtn,poisonousFoodRespawnBtn,backBtn])
        game.showMenuItems(menuItems)
        if game.isKey(pg.K_UP):
            if game.menuPointingTo == 0: game.menuPointingTo = len(menuItems)-1
            else: game.menuPointingTo -= 1
        if game.isKey(pg.K_DOWN):
            if game.menuPointingTo == len(menuItems)-1: game.menuPointingTo = 0
            else: game.menuPointingTo += 1
        if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(colorPlayer1Btn):
            game.getPlayerNextColor(0)
            if game.player1Color == game.player2Color: 
                game.getPlayerNextColor(1)
            game.setConfig('GAMEPLAY', 'player1Color', get_key(game.player1Color, snakeColors))
            game.setConfig('GAMEPLAY', 'player2Color', get_key(game.player2Color, snakeColors))
        if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(wallMode): 
            game.portalWalls = not game.portalWalls
            val = 'True' if game.portalWalls == True else 'False'
            game.setConfig('GAMEPLAY', 'portalWalls', val)
        if game.multiplayer:
            if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(colorPlayer2Btn): 
                game.getPlayerNextColor(1)
                game.setConfig('GAMEPLAY', 'player2Color', get_key(game.player2Color, snakeColors))
        if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(multiplayerOn): 
            game.multiplayer = not game.multiplayer
            val = 'True' if game.multiplayer == True else 'False'
            game.setConfig('GAMEPLAY', 'player1Color', get_key(game.player1Color, snakeColors))
            game.setConfig('GAMEPLAY', 'player2Color', get_key(game.player2Color, snakeColors))
            game.setConfig('GAMEPLAY', 'multiplayer', val)
        if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(speedIncAfterEatBtn): 
            game.speedIncAfterEat = not game.speedIncAfterEat
            val = 'True' if game.speedIncAfterEat == True else 'False'
            game.setConfig('GAMEPLAY', 'speedIncAfterEat', val)
        if game.isKey(pg.K_RIGHT) and game.menuPointingTo == menuItems.index(poisonousFoodCountBtn):
            if game.poisonousFoodCount < game.foodLimit: game.poisonousFoodCount += 1
            game.setConfig('GAMEPLAY', 'poisonousFoodCount', str(game.foodCount))
        if game.isKey(pg.K_LEFT) and game.menuPointingTo == menuItems.index(poisonousFoodCountBtn):
            if game.poisonousFoodCount > 1: game.poisonousFoodCount -= 1
            game.setConfig('GAMEPLAY', 'poisonousFoodCount', str(game.poisonousFoodCount))
        if game.isKey(pg.K_LEFT) and game.menuPointingTo == menuItems.index(foodCountBtn):
            if game.foodCount > 1: game.foodCount -= 1
            game.setConfig('GAMEPLAY', 'foodCount', str(game.foodCount))
        if game.isKey(pg.K_RIGHT) and game.menuPointingTo == menuItems.index(foodCountBtn):
            if game.foodCount < game.foodLimit: game.foodCount += 1
            game.setConfig('GAMEPLAY', 'foodCount', str(game.foodCount))
        if game.isKey(pg.K_RIGHT) and game.menuPointingTo == menuItems.index(initialSpeedBtn):
            if game.initialSpeed < maxInitialSpeed: game.initialSpeed += 1
            game.setConfig('GAMEPLAY', 'initialSpeed', str(game.initialSpeed))
        if game.isKey(pg.K_LEFT) and game.menuPointingTo == menuItems.index(initialSpeedBtn):
            if game.initialSpeed > 1: game.initialSpeed -= 1
            game.setConfig('GAMEPLAY', 'initialSpeed', str(game.initialSpeed))
        if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(poisonousFoodRespawnBtn): 
            game.poisonousFoodRespawn = not game.poisonousFoodRespawn
            val = 'True' if game.poisonousFoodRespawn == True else 'False'
            game.setConfig('GAMEPLAY', 'poisonousFoodRespawn', val)
        if game.isKey(pg.K_RETURN) and game.menuPointingTo == menuItems.index(backBtn): break
        game.update()

def nameField():
    game.player1EnteredName = ''
    game.player2EnteredName = ''
    while True:
        game.onUpdate().setBackground()
        menuItems = []
        player1NameField = game.createMenuItem(f'{"PLAYER 1 " if game.multiplayer else ""}NICKNAME (MAX 10): {game.player1EnteredName}')
        menuItems.extend([player1NameField])
        game.showMenuItems(menuItems,False)
        if game.isQuit(False): quit()
        if game.isKey(pg.K_ESCAPE): 
            game.player1EnteredName = ''
            break
        if game.isAnyKey():
            if game.isKey(pg.K_RETURN) and len(game.player1EnteredName) > 0: break
            if game.isKey(pg.K_BACKSPACE): game.player1EnteredName = game.player1EnteredName[:-1]
            key = game.getKey()
            if (key.isalpha() or key.isdigit()) and len(game.player1EnteredName) < 10: game.player1EnteredName += key.upper()
        game.update()
    if game.multiplayer:
        while True:
            game.onUpdate().setBackground()
            menuItems = []
            player2NameField = game.createMenuItem(f'PLAYER 2 NICKNAME (MAX 10): {game.player2EnteredName}')
            menuItems.extend([player2NameField])
            game.showMenuItems(menuItems,False)
            if game.isQuit(False): quit()
            if game.isKey(pg.K_ESCAPE): 
                game.player1EnteredName, game.player2EnteredName = '',''
                break
            if game.isAnyKey():
                if game.isKey(pg.K_RETURN) and len(game.player2EnteredName) > 0: break
                if game.isKey(pg.K_BACKSPACE): game.player2EnteredName = game.player2EnteredName[:-1]
                key = game.getKey()
                if (key.isalpha() or key.isdigit()) and len(game.player2EnteredName) < 10: game.player2EnteredName += key.upper()
            game.update()
    if not game.multiplayer and len(game.player1EnteredName) > 0:
        game.storeScore(game.player1EnteredName,(game.player1Score-1)*10)
    if game.multiplayer and len(game.player1EnteredName) > 0 and len(game.player2EnteredName) > 0:
        game.storeScore(game.player1EnteredName,(game.player1Score-1)*10,game.player2EnteredName,(game.player2Score-1)*10)

# Starting the game's main loop
while True:
    gameMenu()
    main()

