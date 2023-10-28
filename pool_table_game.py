import random
import copy
import pygame as pg
import numpy as np

# pygame setup
pg.init()  # pygame setup
screen = pg.display.set_mode((1280, 720))
shield = pg.Surface((1000, 600))
reflector = pg.Surface((950, 550))
gameboard = pg.Surface((900, 500))
start_button = pg.Surface((75, 50))
reset_button = pg.Surface((75, 50))
quit_button = pg.Surface((75, 50))
game_over_message = pg.Surface((600, 300))
poison_meter = pg.Surface((75, 50))
poison_down = pg.Surface((25, 25))
poison_up = pg.Surface((25, 25))
coolant_flow_meter_label = pg.Surface((100, 25))
poison_meter_label = pg.Surface((100, 25))
coolant_flow_meter = pg.Surface((75, 50))
coolant_flow_down = pg.Surface((25, 25))
coolant_flow_up = pg.Surface((25, 25))

clock = pg.time.Clock()

# Booleans
running = True
fuel_to_place = False
moderator_to_place = False
poison_to_place = False
coolant_to_place = False
fuel_cursor_growing = False
moderator_cursor_growing = False
poison_cursor_growing = False
coolant_cursor_growing = False
rxn_started = False
supercritical = False
overheat = False


# colors
poison_color = "brown"
coolant_color = "blue"

# numbers
dt = 0
t = 0
fission_count = []
cursor_size = 0
coolant_flow_rate = 1
poison_effectiveness = 0.1
criticality = 0
max_fissions = 0

# lists
neutrons = []
fuel_spots = []
moderator_spots = []
poison_spots = []
coolant_spots = []
neutron_count = []
hot_spots = []

# cursor
starting_cursor = pg.cursors.Cursor(*pg.cursors.arrow)
pg.mouse.set_cursor(starting_cursor)

# positions, sizes, & velocity
birth_speed = 1000

shield_pos = pg.Vector2(
    (screen.get_width() - shield.get_width()) / 2,
    (screen.get_height() - shield.get_height()) / 2,
)
reflector_pos = pg.Vector2(
    (screen.get_width() - reflector.get_width()) / 2,
    (screen.get_height() - reflector.get_height()) / 2,
)
gameboard_pos = pg.Vector2(
    (screen.get_width() - gameboard.get_width()) / 2,
    (screen.get_height() - gameboard.get_height()) / 2,
)
start_button_pos = pg.Vector2(
    screen.get_width() - 25 - start_button.get_width(),
    (screen.get_height() - 25 - start_button.get_height()),
)
reset_button_pos = pg.Vector2(screen.get_width() - 25 - start_button.get_width(), 50)
quit_button_pos = pg.Vector2(
    screen.get_width() - 25 - start_button.get_width(),
    75 + reset_button.get_height(),
)

# coolant meter
coolant_flow_meter_pos = pg.Vector2(
    start_button_pos.x, (start_button_pos.y - 25 - coolant_flow_meter.get_height())
)
coolant_flow_up_pos = pg.Vector2(
    coolant_flow_meter_pos.x - coolant_flow_up.get_width(), coolant_flow_meter_pos.y
)
coolant_flow_down_pos = pg.Vector2(
    coolant_flow_meter_pos.x - coolant_flow_down.get_width(),
    coolant_flow_meter_pos.y + coolant_flow_up.get_height(),
)
coolant_flow_meter_label_pos = pg.Vector2(
    coolant_flow_up_pos.x,
    coolant_flow_meter_pos.y - coolant_flow_meter_label.get_height(),
)

# poison meter
poison_meter_pos = pg.Vector2(
    start_button_pos.x,
    (coolant_flow_meter_label_pos.y - 25 - poison_meter.get_height()),
)
poison_up_pos = pg.Vector2(
    coolant_flow_meter_pos.x - poison_up.get_width(), poison_meter_pos.y
)
poison_down_pos = pg.Vector2(
    coolant_flow_meter_pos.x - poison_down.get_width(),
    poison_meter_pos.y + poison_up.get_height(),
)
poison_meter_label_pos = pg.Vector2(
    poison_up_pos.x, poison_meter_pos.y - poison_meter_label.get_height()
)

game_over_message_pos = pg.Vector2(
    (screen.get_width() - game_over_message.get_width()) / 2,
    (screen.get_height() - game_over_message.get_height()) / 2,
)


neutron_size = 10
starting_pos = pg.Vector2(gameboard.get_width() / 2, gameboard.get_height() / 2)

fuel_button_size = 50
fuel_button_pos = pg.Vector2(75, 150)

moderator_button_size = 50
moderator_button_pos = pg.Vector2(75, 300)

poison_button_size = 50
poison_button_pos = pg.Vector2(75, 450)

coolant_button_size = 50
coolant_button_pos = pg.Vector2(75, 600)


# functions
def bounce(neutron, direction):
    if direction == "bottom":
        neutron["velocity"].y = -abs(neutron["velocity"].y)
    if direction == "top":
        neutron["velocity"].y = abs(neutron["velocity"].y)
    if direction == "right":
        neutron["velocity"].x = -abs(neutron["velocity"].x)
    if direction == "left":
        neutron["velocity"].x = abs(neutron["velocity"].x)
    return neutron


def birth():
    global starting_pos
    new_neutron = {}
    new_neutron["position"] = copy.deepcopy(starting_pos)
    theta = 2 * np.pi * random.random()
    new_neutron["velocity"] = pg.Vector2(
        birth_speed * np.cos(theta), birth_speed * np.sin(theta)
    )
    neutrons.append(new_neutron)


def moderated_bounce(moderator, neutron, i):
    global running
    slowing_factor = 0.5 + 0.5 * random.random()
    tangentVector = {}
    tangentVector["y"] = -(moderator["position"].x - neutron["velocity"].x)
    tangentVector["x"] = moderator["position"].y - neutron["velocity"].y
    a = moderator["position"].x - neutron["position"].x
    b = moderator["position"].y - neutron["position"].y
    theta1 = np.arctan(b / a)
    theta2 = np.arctan(neutron["velocity"].y / neutron["velocity"].x)
    speed = (neutron["velocity"].y ** 2 + neutron["velocity"].x ** 2) ** 0.5
    phi = np.pi - theta1 - theta2
    neutron["position"].x -= 2 * neutron["velocity"].x * dt
    neutron["position"].y -= 2 * neutron["velocity"].y * dt
    neutron["velocity"].x = abs(a) / a * slowing_factor * speed * np.cos(phi)
    neutron["velocity"].y = -abs(b) / b * slowing_factor * speed * np.sin(phi)
    if speed < 100:
        death(i)
    return neutron


def fission(spot, index):
    death(index)
    hot_spots.append({"position": spot["position"], "size": 0})
    birth()
    birth()


def death(index):
    del neutrons[i]


def grow_cursor(name, spot_color):
    global cursor_size
    cursor_size += 1
    surf = pg.Surface((cursor_size, cursor_size))  # you could also load an image
    surf.fill("white")  # and use that as your surface
    pg.draw.circle(
        surf, spot_color, (int(cursor_size / 2), int(cursor_size / 2)), cursor_size / 2
    )
    font = pg.font.Font(None, 12)
    text = font.render(name, True, "white")
    textpos = text.get_rect(centerx=int(cursor_size / 2), y=int(cursor_size / 2))
    surf.blit(text, textpos)
    color = pg.cursors.Cursor((int(cursor_size / 2), int(cursor_size / 2)), surf)
    pg.mouse.set_cursor(color)


def place_spot(spot_type):
    global cursor_size
    global fuel_to_place
    new_x = event.pos[0] - gameboard_pos.x
    new_y = event.pos[1] - gameboard_pos.y
    new_pos = pg.Vector2((new_x, new_y))
    if (
        new_x > 0
        and new_x < gameboard.get_width()
        and new_y > 0
        and new_y < gameboard.get_height()
    ):
        spot_type.append({"position": new_pos, "size": cursor_size / 2})
    pg.mouse.set_cursor(starting_cursor)


def place_coolant():
    global cursor_size
    global fuel_to_place
    new_x = event.pos[0] - gameboard_pos.x
    new_y = event.pos[1] - gameboard_pos.y
    new_pos = pg.Vector2((new_x, new_y))
    if (
        new_x > 0
        and new_x < gameboard.get_width()
        and new_y > 0
        and new_y < gameboard.get_height()
    ):
        coolant_spots.append(
            {"position": new_pos, "size": cursor_size / 2, "at_capacity": 0}
        )
    pg.mouse.set_cursor(starting_cursor)


def touching_circle(position1, position2, size1, size2=0):
    return (
        (position1.x - position2.x) ** 2 + (position1.y - position2.y) ** 2
    ) ** 0.5 < size1 + size2


def touching_rectrangle(surface1, position1, position2):
    return (
        position1.x < position2.x
        and position1.x + surface1.get_width() > position2.x
        and position1.y < position2.y
        and position1.y + surface1.get_height() > position2.y
    )


def add_text(string, pos, surface, color="white", fontsize=30):
    font = pg.font.Font(None, fontsize)
    text = font.render(string, True, color)
    textpos = text.get_rect(centerx=pos.x, centery=pos.y)

    surface.blit(text, textpos)


def reset_game():
    global fission_count
    global t
    global criticality
    global poison_effectiveness
    global coolant_flow_rate
    global neutrons
    global fuel_spots
    global moderator_spots
    global poison_spots
    global coolant_spots
    global neutron_count
    global supercritical
    global overheat
    global rxn_started
    global hot_spots
    fission_count = []
    t = 0
    criticality = 0
    poison_effectiveness = 0.1
    coolant_flow_rate = 1
    hot_spots = []
    neutrons = []
    fuel_spots = []
    moderator_spots = []
    poison_spots = []
    coolant_spots = []
    neutron_count = []
    supercritical = False
    overheat = False
    rxn_started = False


while running:
    # poll for events
    # pg.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            click_pos = pg.Vector2(event.pos[0], event.pos[1])
            if rxn_started == False:
                if touching_circle(click_pos, fuel_button_pos, fuel_button_size):
                    cursor_size = 0
                    fuel_cursor_growing = True
                if touching_circle(
                    click_pos, moderator_button_pos, moderator_button_size
                ):
                    cursor_size = 0
                    moderator_cursor_growing = True
                if touching_circle(click_pos, poison_button_pos, poison_button_size):
                    cursor_size = 0
                    poison_cursor_growing = True
                if touching_circle(click_pos, coolant_button_pos, coolant_button_size):
                    cursor_size = 0
                    coolant_cursor_growing = True
            if (
                touching_rectrangle(start_button, start_button_pos, click_pos)
                and rxn_started == False
            ):
                rxn_started = True
                for i in range(50):
                    birth()
            if touching_rectrangle(reset_button, reset_button_pos, click_pos):
                reset_game()
            if touching_rectrangle(quit_button, quit_button_pos, click_pos):
                running = False
            if touching_rectrangle(poison_up, poison_up_pos, click_pos):
                poison_effectiveness += 0.01
            if touching_rectrangle(poison_down, poison_down_pos, click_pos):
                poison_effectiveness -= 0.01
            if touching_rectrangle(coolant_flow_up, coolant_flow_up_pos, click_pos):
                coolant_flow_rate += 0.01
            if touching_rectrangle(coolant_flow_down, coolant_flow_down_pos, click_pos):
                coolant_flow_rate -= 0.01

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
            if coolant_cursor_growing == True:
                coolant_cursor_growing = False
                coolant_to_place = True
            elif coolant_to_place == True:
                place_coolant()
                coolant_to_place = False
    # grow the cursor
    if fuel_cursor_growing:
        grow_cursor("f", "black")

    if moderator_cursor_growing:
        grow_cursor("m", "purple")

    if poison_cursor_growing:
        grow_cursor("p", poison_color)
    if coolant_cursor_growing:
        grow_cursor("c", coolant_color)
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("yellow")
    gameboard.fill("white")
    shield.fill("gray")
    reflector.fill("green")
    start_button.fill("orange")
    reset_button.fill("orange")
    quit_button.fill("orange")
    poison_meter.fill("white")
    coolant_flow_meter.fill("white")
    poison_meter_label.fill("orange")
    coolant_flow_meter_label.fill("orange")
    poison_up.fill("brown")
    coolant_flow_up.fill("brown")
    poison_down.fill("brown")
    coolant_flow_down.fill("brown")
    add_text(
        "criticality:" + str(0.01 * int(100 * criticality)),
        pg.Vector2(screen.get_width() / 2, 10),
        screen,
        "black",
    )
    add_text(
        "operation time:" + str(int(t)) + " seconds",
        pg.Vector2(screen.get_width() - 200, 10),
        screen,
        "black",
    )

    add_text(
        "neutrons:" + str(len(neutrons)),
        pg.Vector2(screen.get_width() / 2, 40),
        screen,
        "black",
    )
    add_text("shielding", pg.Vector2(shield.get_width() / 2, 10), shield, "black")
    add_text("reflector", pg.Vector2(reflector.get_width() / 2, 10), reflector, "black")
    add_text("matrix", pg.Vector2(gameboard.get_width() / 2, 10), gameboard, "black")
    add_text(
        "start",
        pg.Vector2(start_button.get_width() / 2, start_button.get_height() / 2),
        start_button,
        "black",
    )
    add_text(
        "reset",
        pg.Vector2(reset_button.get_width() / 2, reset_button.get_height() / 2),
        reset_button,
        "black",
    )
    add_text(
        "quit",
        pg.Vector2(quit_button.get_width() / 2, quit_button.get_height() / 2),
        quit_button,
        "black",
    )
    add_text(
        str(int(poison_effectiveness * 100)) + "%",
        pg.Vector2(poison_meter.get_width() / 2, poison_meter.get_height() / 2),
        poison_meter,
        "black",
    )
    add_text(
        str(int(coolant_flow_rate * 100)) + "%",
        pg.Vector2(
            coolant_flow_meter.get_width() / 2, coolant_flow_meter.get_height() / 2
        ),
        coolant_flow_meter,
        "black",
    )
    add_text(
        "^",
        pg.Vector2(poison_up.get_width() / 2, poison_up.get_height() / 2),
        poison_up,
        "black",
    )
    add_text(
        "^",
        pg.Vector2(coolant_flow_up.get_width() / 2, coolant_flow_up.get_height() / 2),
        coolant_flow_up,
        "black",
    )
    add_text(
        "v",
        pg.Vector2(poison_down.get_width() / 2, poison_down.get_height() / 2),
        poison_down,
        "black",
    )
    add_text(
        "v",
        pg.Vector2(
            coolant_flow_down.get_width() / 2, coolant_flow_down.get_height() / 2
        ),
        coolant_flow_down,
        "black",
    )
    add_text(
        "poison insertion",
        pg.Vector2(
            poison_meter_label.get_width() / 2, poison_meter_label.get_height() / 2
        ),
        poison_meter_label,
        "black",
        fontsize=15,
    )
    add_text(
        "coolant flow rate",
        pg.Vector2(
            coolant_flow_meter_label.get_width() / 2,
            coolant_flow_meter_label.get_height() / 2,
        ),
        coolant_flow_meter_label,
        "black",
        fontsize=15,
    )

    for spot in fuel_spots:
        fuel_spot = pg.draw.circle(gameboard, "black", spot["position"], spot["size"])
        add_text("f", spot["position"], gameboard, fontsize=12)

    pg.draw.circle(screen, "black", fuel_button_pos, fuel_button_size)
    add_text("fuel", fuel_button_pos, screen)

    for spot in moderator_spots:
        moderator_spot = pg.draw.circle(
            gameboard, "purple", spot["position"], spot["size"]
        )
        add_text("m", spot["position"], gameboard, fontsize=12)

    pg.draw.circle(screen, "purple", moderator_button_pos, moderator_button_size)
    add_text("moderator", moderator_button_pos, screen)

    for spot in poison_spots:
        poison_spot = pg.draw.circle(
            gameboard,
            poison_color,
            spot["position"],
            spot["size"] * poison_effectiveness,
        )
        add_text("p", spot["position"], gameboard, fontsize=12)

    pg.draw.circle(screen, poison_color, poison_button_pos, poison_button_size)
    add_text("poison", poison_button_pos, screen)

    for spot in coolant_spots:
        coolant_spot = pg.draw.circle(
            gameboard, coolant_color, spot["position"], spot["size"]
        )
        add_text("c", spot["position"], gameboard, fontsize=12)

    pg.draw.circle(screen, coolant_color, coolant_button_pos, coolant_button_size)
    add_text("coolant", coolant_button_pos, screen)

    i = 0
    fissions_this_step = 0
    for neutron in neutrons:
        pg.draw.circle(gameboard, "red", neutron["position"], neutron_size)
        if neutron["position"].y > gameboard.get_height():
            neutron = bounce(neutron, "bottom")
        if neutron["position"].y < 0:
            neutron = bounce(neutron, "top")
        if neutron["position"].x > gameboard.get_width():
            neutron = bounce(neutron, "right")
        if neutron["position"].x < 0:
            neutron = bounce(neutron, "left")
        for fuel in fuel_spots:
            if touching_circle(
                neutron["position"], fuel["position"], neutron_size, fuel["size"]
            ):
                if (
                    neutron["velocity"].x ** 2 + neutron["velocity"].y ** 2
                ) ** 0.5 < birth_speed / 2:
                    fission(fuel, i)
                    fissions_this_step += 1
        for moderator in moderator_spots:
            if touching_circle(
                neutron["position"],
                moderator["position"],
                neutron_size,
                moderator["size"],
            ):
                neutron = moderated_bounce(moderator, neutron, i)
        for poison in poison_spots:
            if (
                touching_circle(
                    neutron["position"],
                    poison["position"],
                    neutron_size,
                    poison["size"] * poison_effectiveness,
                )
                and poison_effectiveness > 0
            ):
                death(i)
        i += 1
        neutron["position"].x += neutron["velocity"].x * dt
        neutron["position"].y += neutron["velocity"].y * dt
    i = 0

    fission_count.append(fissions_this_step)
    if len(fission_count) > 1000:
        fission_count.pop(0)
    if len(fission_count) > 2:
        power_level = sum(fission_count)
        max_fissions = max(max_fissions, power_level)

    if rxn_started:
        for heat in hot_spots:
            heat["size"] += 1
            pg.draw.circle(gameboard, "pink", heat["position"], heat["size"])
            for coolant in coolant_spots:
                if (
                    touching_circle(
                        heat["position"],
                        coolant["position"],
                        heat["size"],
                        coolant["size"],
                    )
                    and coolant["at_capacity"] < 1
                ):
                    del hot_spots[i]
                    coolant["at_capacity"] = 1000 / coolant["size"]
            i += 1
        for coolant in coolant_spots:
            if coolant_flow_rate > 0:
                coolant_flow_rate -= (1 - coolant["at_capacity"]) / 1000000
            else:
                coolant_flow_rate = 0
            coolant["at_capacity"] -= 1

    screen.blit(shield, shield_pos)
    screen.blit(reflector, reflector_pos)
    screen.blit(gameboard, gameboard_pos)
    screen.blit(start_button, start_button_pos)
    screen.blit(quit_button, quit_button_pos)
    screen.blit(reset_button, reset_button_pos)
    screen.blit(poison_meter, poison_meter_pos)
    screen.blit(coolant_flow_meter, coolant_flow_meter_pos)
    screen.blit(poison_meter_label, poison_meter_label_pos)
    screen.blit(coolant_flow_meter_label, coolant_flow_meter_label_pos)
    screen.blit(poison_up, poison_up_pos)
    screen.blit(coolant_flow_up, coolant_flow_up_pos)
    screen.blit(poison_down, poison_down_pos)
    screen.blit(coolant_flow_down, coolant_flow_down_pos)

    # flip() the display to put your work on screen
    pg.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000
    if rxn_started:
        t += dt
    neutron_count.append(len(neutrons))
    if len(neutron_count) > 75:
        neutron_count.pop(0)
    if len(neutron_count) > 2:
        if neutron_count[0] > 50:
            criticality = neutron_count[-1] / neutron_count[0]
            if criticality > 1.2:
                supercritical = True

    total_hotspot_area = 0
    for heat in hot_spots:
        total_hotspot_area += heat["size"]
    if total_hotspot_area > screen.get_width():
        overheat = True

    while supercritical == True:
        game_over_message.fill("yellow")
        add_text(
            "Oh no! Your reactor has reached uncontrollable supercricitacality.",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 - 75,
            ),
            game_over_message,
            "black",
            25,
        )
        add_text(
            "Total Operation Time: " + str(int(t)) + " seconds.",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 - 50,
            ),
            game_over_message,
            "black",
            25,
        )
        add_text(
            "Maximum Power Level: " + str(int(max_fissions * 200)) + " MeV/second",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 - 25,
            ),
            game_over_message,
            "black",
            25,
        )
        add_text(
            "Game Over",
            pg.Vector2(
                game_over_message.get_width() / 2, game_over_message.get_height() / 2
            ),
            game_over_message,
            "black",
            50,
        )
        add_text(
            "Click anywhere to restart.",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 + 50,
            ),
            game_over_message,
            "black",
            25,
        )
        screen.blit(game_over_message, game_over_message_pos)
        pg.display.flip()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                reset_game()

    while rxn_started == True and len(neutrons) == 0:
        game_over_message.fill("yellow")
        add_text(
            "Oh no! Your reactor has run out of neutrons.",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 - 75,
            ),
            game_over_message,
            "black",
            25,
        )
        add_text(
            "Total Operation Time: " + str(int(t)) + " seconds.",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 - 50,
            ),
            game_over_message,
            "black",
            25,
        )
        add_text(
            "Maximum Power Level: " + str(int(max_fissions * 200)) + " MeV/second",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 - 25,
            ),
            game_over_message,
            "black",
            25,
        )
        add_text(
            "Game Over",
            pg.Vector2(
                game_over_message.get_width() / 2, game_over_message.get_height() / 2
            ),
            game_over_message,
            "black",
            50,
        )
        add_text(
            "Click anywhere to restart.",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 + 50,
            ),
            game_over_message,
            "black",
            25,
        )
        screen.blit(game_over_message, game_over_message_pos)
        pg.display.flip()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                reset_game()

    while overheat == True:
        game_over_message.fill("yellow")
        add_text(
            "Oh no! Your fuel has overheated.",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 - 75,
            ),
            game_over_message,
            "black",
            25,
        )
        add_text(
            "Total Operation Time: " + str(int(t)) + " seconds.",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 - 50,
            ),
            game_over_message,
            "black",
            25,
        )
        add_text(
            "Maximum Power Level: " + str(int(max_fissions * 200)) + " MeV/second",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 - 25,
            ),
            game_over_message,
            "black",
            25,
        )
        add_text(
            "Game Over",
            pg.Vector2(
                game_over_message.get_width() / 2, game_over_message.get_height() / 2
            ),
            game_over_message,
            "black",
            50,
        )
        add_text(
            "Click anywhere to restart.",
            pg.Vector2(
                game_over_message.get_width() / 2,
                game_over_message.get_height() / 2 + 50,
            ),
            game_over_message,
            "black",
            25,
        )
        screen.blit(game_over_message, game_over_message_pos)
        pg.display.flip()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                reset_game()
        print("still here")
pg.quit()
