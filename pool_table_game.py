import pygame as  pg
import numpy as np
import random
import copy

# pygame setup
pg.init()# pygame setup
screen = pg.display.set_mode((1280, 720))
gameboard = pg.Surface((900, 500))
clock = pg.time.Clock()

# Booleans
running = True
fuel_to_place = False
moderator_to_place = False
poison_to_place = False
fuel_cursor_growing = False
moderator_cursor_growing = False
poison_cursor_growing = False

# numbers
dt = 0
fission_count = 0
cursor_size = 0

# lists
neutrons = []
fuel_spots = []
moderator_spots = []
poison_spots = []

# cursor
starting_cursor = pg.cursors.Cursor(*pg.cursors.arrow)
pg.mouse.set_cursor(starting_cursor)

# positions, sizes, & velocity
birth_speed = 1000

gameboard_pos = pg.Vector2((screen.get_width()-gameboard.get_width()) / 2, (screen.get_height()-gameboard.get_height()) / 2)

neutron_size = 10
starting_pos = pg.Vector2(gameboard.get_width() / 2, gameboard.get_height() / 2)

fuel_button_size = 50
fuel_button_pos = pg.Vector2(100,150)

moderator_button_size = 50
moderator_button_pos = pg.Vector2(100,300)

poison_button_size = 50
poison_button_pos = pg.Vector2(100,450)

# functions
def bounce(neutron,direction):    
    if direction == 'bottom':
        neutron['velocity'].y = -abs(neutron['velocity'].y)
    if direction == 'top':
        neutron['velocity'].y = abs(neutron['velocity'].y)
    if direction =='right':
        neutron['velocity'].x = -abs(neutron['velocity'].x)
    if direction =='left':
        neutron['velocity'].x =  abs(neutron['velocity'].x)
    return neutron
        
def birth():
    global starting_pos
    new_neutron = {}
    new_neutron['position'] = copy.deepcopy(starting_pos)
    theta = 2 * np.pi*random.random()
    new_neutron['velocity'] = pg.Vector2(birth_speed*np.cos(theta),birth_speed*np.sin(theta))
    neutrons.append(new_neutron)
    
def moderated_bounce(moderator,neutron,i):
    global running
    slowing_factor = 0.5 + 0.5*random.random()
    tangentVector = {}
    tangentVector['y'] = -( moderator['position'].x - neutron['velocity'].x )
    tangentVector['x'] = moderator['position'].y - neutron['velocity'].y
    a = moderator['position'].x - neutron['position'].x
    b = moderator['position'].y - neutron['position'].y
    theta1 = np.arctan(b/a)
    theta2 = np.arctan(neutron['velocity'].y/neutron['velocity'].x)
    speed = (neutron['velocity'].y**2+neutron['velocity'].x**2)**0.5
    phi = np.pi - theta1 - theta2
    neutron['position'].x -= 2*neutron['velocity'].x * dt
    neutron['position'].y -= 2*neutron['velocity'].y * dt
    neutron['velocity'].x = abs(a)/a * slowing_factor * speed * np.cos(phi)
    neutron['velocity'].y = -abs(b)/b  * slowing_factor * speed * np.sin(phi)
    if speed < 100:
        death(i)
    return neutron
        
def fission(index):
    global fission_count
    death(index)
    birth()
    birth()
    fission_count += 1
    
def death(index):
    del(neutrons[i])
    
def grow_cursor(name,spot_color):
    global cursor_size
    cursor_size += 1
    surf = pg.Surface((cursor_size,cursor_size)) # you could also load an image 
    surf.fill("white")        # and use that as your surface
    pg.draw.circle(surf,spot_color, (int(cursor_size/2),int(cursor_size/2)), cursor_size/2)
    font = pg.font.Font(None, 30)
    text = font.render(name, True, "white")
    textpos = text.get_rect(centerx=int(cursor_size/2), y=int(cursor_size/2))
    surf.blit(text, textpos) 
    color = pg.cursors.Cursor((int(cursor_size/2),int(cursor_size/2)), surf)
    pg.mouse.set_cursor(color)
    
def place_spot(spot_type):   
    global cursor_size
    global fuel_to_place
    new_x = event.pos[0] - gameboard_pos.x
    new_y = event.pos[1] - gameboard_pos.y
    new_pos = pg.Vector2((new_x,new_y))
    if new_x > 0 and new_x < gameboard.get_width() and new_y > 0 and new_y < gameboard.get_height():
        spot_type.append({'position':new_pos,'size':cursor_size/2})     
    pg.mouse.set_cursor(starting_cursor)
    
def touching_circle(position1,position2,size1,size2=0):
    return ((position1.x - position2.x) **2 + (position1.y - position2.y)**2)**0.5 < size1 + size2

def add_text(string,pos,surface,color="white"):
    font = pg.font.Font(None, 30)
    text = font.render(string, True, color)
    textpos = text.get_rect(centerx=pos.x, y=pos.y)
    surface.blit(text, textpos)    
    
birth()
while running:
    # poll for events
    # pg.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            click_pos =  pg.Vector2((event.pos[0],event.pos[1]))
            if touching_circle(click_pos,fuel_button_pos,fuel_button_size):
                cursor_size = 0
                fuel_cursor_growing = True
            if touching_circle(click_pos,moderator_button_pos,moderator_button_size):
                cursor_size = 0
                moderator_cursor_growing = True
            if touching_circle(click_pos,poison_button_pos,poison_button_size):
                cursor_size = 0
                poison_cursor_growing = True
        elif event.type == pg.MOUSEBUTTONUP:
            if fuel_cursor_growing == True:
                fuel_cursor_growing = False
                fuel_to_place = True
            elif fuel_to_place == True:
                place_spot(fuel_spots)
                fuel_to_place = False
            if moderator_cursor_growing == True:
                moderator_cursor_growing = False
                moderator_to_place = True
            elif moderator_to_place == True:
                place_spot(moderator_spots)
                moderator_to_place = False  
            if poison_cursor_growing == True:
                poison_cursor_growing = False
                poison_to_place = True
            elif poison_to_place == True:
                place_spot(poison_spots)
                poison_to_place = False                      
    # grow the cursor
    if fuel_cursor_growing: 
        grow_cursor("fuel","black")
    
    if moderator_cursor_growing: 
        grow_cursor("moderator","purple")
        
    if poison_cursor_growing: 
        grow_cursor("poison","green")
        
        
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("yellow")     
    gameboard.fill("white")
    add_text("fissions:" + str(fission_count),pg.Vector2(screen.get_width() / 2, 10),screen,'black')
    add_text("neutrons:" + str(len(neutrons)),pg.Vector2(screen.get_width() / 2, 40),screen,'black')

    for spot in fuel_spots:
        fuel_spot = pg.draw.circle(gameboard, "black", spot['position'], spot['size'])
        add_text("fuel",spot['position'],gameboard)
   
    pg.draw.circle(screen, "black", fuel_button_pos, fuel_button_size)
    add_text("fuel",fuel_button_pos,screen)
    
    for spot in moderator_spots:
        moderator_spot = pg.draw.circle(gameboard, "purple", spot['position'], spot['size'])
        add_text("moderator",spot['position'],gameboard)
    
    pg.draw.circle(screen, "purple", moderator_button_pos, moderator_button_size)
    add_text("moderator",moderator_button_pos,screen)
    
    for spot in poison_spots:
        poison_spot = pg.draw.circle(gameboard, "green", spot['position'], spot['size'])
        add_text("poison",spot['position'],gameboard)
    
    pg.draw.circle(screen, "green", poison_button_pos, poison_button_size)
    add_text("poison",poison_button_pos,screen)
    
            
    i = 0
    for neutron in neutrons:    
        pg.draw.circle(gameboard, "red", neutron['position'],neutron_size)
        if neutron['position'].y >  gameboard.get_height():
            neutron = bounce(neutron,'bottom')
        if neutron['position'].y < 0:
            neutron = bounce(neutron,'top')
        if neutron['position'].x > gameboard.get_width():
            neutron = bounce(neutron,'right')
        if neutron['position'].x < 0:
            neutron = bounce(neutron,'left')
        for fuel in fuel_spots:
            if touching_circle(neutron['position'],fuel['position'],neutron_size,fuel['size']):
                if (neutron['velocity'].x**2 + neutron['velocity'].y**2)**0.5 < birth_speed/2:
                    fission(i)
        for moderator in moderator_spots:
            if touching_circle(neutron['position'],moderator['position'],neutron_size,moderator['size']):
                neutron = moderated_bounce(moderator,neutron,i)
        for poison in poison_spots:
            if touching_circle(neutron['position'],poison['position'],neutron_size,poison['size']):
                death(i)
        i += 1        
        neutron['position'].x += neutron['velocity'].x * dt
        neutron['position'].y += neutron['velocity'].y * dt

    screen.blit(gameboard,gameboard_pos) 

    # flip() the display to put your work on screen
    pg.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pg.quit()