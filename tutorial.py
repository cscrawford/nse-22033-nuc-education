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
reset_gameboard_button = pg.Surface((75, 50))
reset_neutrons_button = pg.Surface((75, 50))
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
message_box = pg.Surface((700, 50))

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
fuel_tutorial_step_is_passed = False


# colors
coolant_color = "blue"

# numbers
dt = 0
t = 0
fission_count = []
cursor_size = 0
coolant_flow_rate = 1
poison_effectiveness = 1
criticality = 0
max_fissions = 0
tutorial_step = 0
iter = 0

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
message_box_pos = pg.Vector2(
    (screen.get_width() / 2 - message_box.get_width() / 2),
    (screen.get_height() - message_box.get_height() - 5),
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
reset_gameboard_button_pos = pg.Vector2(
    screen.get_width() - 25 - start_button.get_width(), 50
)
reset_neutrons_button_pos = pg.Vector2(
    screen.get_width() - 25 - start_button.get_width(),
    75 + reset_gameboard_button.get_height(),
)
quit_button_pos = pg.Vector2(
    screen.get_width() - 25 - start_button.get_width(),
    100 + reset_neutrons_button.get_height() + reset_gameboard_button.get_height(),
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

place_here_size = 30
first_mod_pos = pg.Vector2(gameboard.get_width() * 3 / 4, gameboard.get_height() / 2)
first_fuel_pos = pg.Vector2(gameboard.get_width() / 4, first_mod_pos.y)
fist_coolant_pos = pg.Vector2(first_fuel_pos.x + place_here_size + 5, first_fuel_pos.y)


# functions


def reset_cursor():
    global coolant_to_place
    global poison_to_place
    global moderator_to_place
    global fuel_to_place
    pg.mouse.set_cursor(starting_cursor)
    coolant_to_place = False
    poison_to_place = False
    moderator_to_place = False
    fuel_to_place = False


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


def primary_birth():
    global starting_pos
    new_neutron = {}
    new_neutron["position"] = copy.deepcopy(starting_pos)
    new_neutron["velocity"] = pg.Vector2(birth_speed, 0)
    neutrons.append(new_neutron)


def secondary_birth():
    new_neutron = {}
    new_neutron["position"] = pg.Vector2(
        random.random() * gameboard.get_width(),
        random.random() * gameboard.get_height(),
    )
    theta = 2 * np.pi * random.random()
    new_neutron["velocity"] = pg.Vector2(
        birth_speed * np.cos(theta), birth_speed * np.sin(theta)
    )
    neutrons.append(new_neutron)


def moderated_bounce(neutron):
    global running
    slowing_factor = 0.25
    neutron["position"].x -= 2 * neutron["velocity"].x * dt
    neutron["position"].y -= 2 * neutron["velocity"].y * dt
    neutron["velocity"].x = -(neutron["velocity"].x) * slowing_factor
    neutron["velocity"].y = -(neutron["velocity"].y) * slowing_factor
    return neutron


def fission(spot, index):
    global hot_spots
    death(index)
    hot_spots.append({"position": spot["position"], "size": 0})
    secondary_birth()
    secondary_birth()


def death(index):
    del neutrons[index]


def grow_cursor(name, spot_color):
    global cursor_size
    reset_cursor()
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


def place_mod():
    global cursor_size
    global fuel_to_place
    moderator_spots.append({"position": first_mod_pos, "size": place_here_size / 2})


def place_fuel():
    global cursor_size
    global fuel_to_place
    fuel_spots.append({"position": first_fuel_pos, "size": place_here_size / 2})


def place_coolant():
    global cursor_size
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


def touching_circle(position1, position2, size1, size2=0):
    return (
        (position1.x - position2.x) ** 2 + (position1.y - position2.y) ** 2
    ) ** 0.5 < size1 + size2


def touching_rectangle(surface1, position1, position2):
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


def reset_neutrons():
    global fission_count
    global t
    global criticality
    global coolant_flow_rate
    global neutrons
    global neutron_count
    global supercritical
    global overheat
    global rxn_started
    global hot_spots
    fission_count = []
    t = 0
    criticality = 0
    coolant_flow_rate = 1
    hot_spots = []
    neutrons = []
    neutron_count = []
    supercritical = False
    overheat = False
    rxn_started = False


def reset_gameboard():
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


def blit_gameboard(message=False):
    global screen, shield, reflector, gameboard, start_button, quit_button, reset_gameboard_button, reset_neutrons_button, poison_meter, coolant_flow_meter, poison_meter_label, coolant_flow_meter_label, poison_up, poison_down, coolant_flow_up, coolant_flow_down, message_box
    global screen, shield_pos, reflector_pos, gameboard_pos, start_button_pos, quit_button_pos, reset_gameboard_button_pos, reset_neutrons_button_pos, poison_meter_pos, coolant_flow_meter_pos, poison_meter_label_pos, coolant_flow_meter_label_pos, poison_up_pos, poison_down_pos, coolant_flow_up_pos, coolant_flow_down_pos, message_box_pos

    screen.blit(shield, shield_pos)
    screen.blit(reflector, reflector_pos)
    screen.blit(gameboard, gameboard_pos)
    screen.blit(start_button, start_button_pos)
    screen.blit(quit_button, quit_button_pos)
    screen.blit(reset_gameboard_button, reset_gameboard_button_pos)
    screen.blit(reset_neutrons_button, reset_neutrons_button_pos)
    screen.blit(poison_meter, poison_meter_pos)
    screen.blit(coolant_flow_meter, coolant_flow_meter_pos)
    screen.blit(poison_meter_label, poison_meter_label_pos)
    screen.blit(coolant_flow_meter_label, coolant_flow_meter_label_pos)
    screen.blit(poison_up, poison_up_pos)
    screen.blit(coolant_flow_up, coolant_flow_up_pos)
    screen.blit(poison_down, poison_down_pos)
    screen.blit(coolant_flow_down, coolant_flow_down_pos)
    if message is not False:
        screen.blit(message_box, message_box_pos)
    # flip() the display to put your work on screen
    pg.display.flip()


def neutron_transport():
    global neutrons
    global moderator_spots, fuel_spots, coolant_spots, poison_spots, hot_spots
    global fissions_this_step
    global coolant_flow_rate

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
                neutron = moderated_bounce(neutron)
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
    if fuel_tutorial_step_is_passed:
        for heat in hot_spots:
            heat["size"] += 1
            pg.draw.circle(gameboard, "pink", heat["position"], heat["size"])
            add_text("heat", heat["position"], gameboard, color="black", fontsize=18)
            for coolant in coolant_spots:
                if (
                    touching_circle(
                        heat["position"],
                        coolant["position"],
                        heat["size"],
                        coolant["size"],
                    )
                    and coolant["at_capacity"] < 1
                ) and len(hot_spots) > 0:
                    del hot_spots[i]
                    coolant["at_capacity"] = 1000 / coolant["size"]
            i += 1
        for coolant in coolant_spots:
            if coolant_flow_rate > 0:
                coolant_flow_rate -= (1 - coolant["at_capacity"]) / 1000000
            else:
                coolant_flow_rate = 0
            coolant["at_capacity"] -= 1


def repaint_gameboard(
    message=False,
):  # fill the screen with a color to wipe away anything from last frame
    global screen, shield, reflector, gameboard, start_button, quit_button, reset_gameboard_button, reset_neutrons_button, poison_meter, coolant_flow_meter, poison_meter_label, coolant_flow_meter_label, poison_up, poison_down, coolant_flow_up, coolant_flow_down, message_box
    global screen, shield_pos, reflector_pos, gameboard_pos, start_button_pos, quit_button_pos, reset_gameboard_button_pos, reset_neutrons_button_pos, poison_meter_pos, coolant_flow_meter_pos, poison_meter_label_pos, coolant_flow_meter_label_pos, poison_up_pos, poison_down_pos, coolant_flow_up_pos, coolant_flow_down_pos, message_box_pos
    global poison_color
    global poison_effectiveness
    global moderator_spots, neutrons
    screen.fill("yellow")
    gameboard.fill("white")
    shield.fill("gray")
    reflector.fill("green")
    start_button.fill("orange")
    reset_gameboard_button.fill("orange")
    reset_neutrons_button.fill("orange")
    quit_button.fill("orange")
    poison_meter.fill("white")
    coolant_flow_meter.fill("white")
    poison_meter_label.fill("orange")
    coolant_flow_meter_label.fill("orange")
    poison_up.fill("brown")
    coolant_flow_up.fill("brown")
    poison_down.fill("brown")
    coolant_flow_down.fill("brown")
    if message is not False:
        message_box.fill("orange")
        add_text(
            message,
            pg.Vector2((message_box.get_width() / 2), message_box.get_height() / 2),
            message_box,
            "black",
        )
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
        "reset gameboard",
        pg.Vector2(
            reset_gameboard_button.get_width() / 2,
            reset_gameboard_button.get_height() / 2,
        ),
        reset_gameboard_button,
        "black",
        fontsize=14,
    )
    add_text(
        "reset neutrons",
        pg.Vector2(
            reset_neutrons_button.get_width() / 2,
            reset_neutrons_button.get_height() / 2,
        ),
        reset_neutrons_button,
        "black",
        fontsize=14,
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
            spot["size"],
        )
        add_text("p", spot["position"], gameboard, fontsize=12)

    pg.draw.circle(
        screen,
        poison_color,
        poison_button_pos,
        poison_button_size,
    )
    add_text("poison", poison_button_pos, screen)

    for spot in coolant_spots:
        coolant_spot = pg.draw.circle(
            gameboard, coolant_color, spot["position"], spot["size"]
        )
        add_text("c", spot["position"], gameboard, fontsize=12)

    pg.draw.circle(screen, coolant_color, coolant_button_pos, coolant_button_size)
    add_text("coolant", coolant_button_pos, screen)

    neutron_transport()

    blit_gameboard(message)


def advance_if_clicked():
    global running
    global tutorial_step
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            click_pos = pg.Vector2(event.pos[0], event.pos[1])
            if touching_rectangle(quit_button, quit_button_pos, click_pos):
                pg.quit()
            else:
                tutorial_step += 1


tutorial_messages = [
    "Welcome to Fission Reactor Modeling!",
    "Ready to find out what happens in a nuclear reactor?",
    "Let's take a look at the game board.",
    "As you can see, the gameboard is labeled matrix.",
    "In a reactor, the matrix holds everything in place.",
    "Surrounding the matrix, you can see there is a reflector.",
    "Neutrons fly around inside a reactor.",
    "When they crash into they nucleus of an atom,",
    "They either stick or bounce.",
    "The reflector is full of bouncy atoms.",
    "When a neutron crashes into a reflector atom...",
    "It bounces back into the reactor!",
    "Surrounding the reflector, you can see there is shielding.",
    "When an atom fissions, what comes out?",
    "Two smaller atoms, two neutrons, a little heat, and a gamma ray!",
    "Gamma rays can pass through most materials.",
    "And if they were to get out of the reactor...",
    "People nearby would be irradiated.",
    "Shielding keeps gamma rays from escaping.",
    "Now, what is the matrix holding in place?",
    "There are four main components:",
    "Fuel, moderator, poison, and coolant.",
    "Let's start with the moderator.",
    "Neutrons from fission are going too fast.",
    "Even if they got close to a fuel atom,",
    "They would fly right past!",
    "Moderator atoms are a little bouncy,",
    "And they slow down the neutrons.",
    "Now how about the fuel?",
    "Most fuel for fission is full of uranium-235 atoms.",
    "Uranium-235 atoms are stable,",
    "But uranium-236 atoms like to fission.",
    "When a neutron crashes into a uranium-235 atom,",
    "It sticks! It gets absorbed into the nucleus",
    "And the atom becomes uranium-236.",
    "You know what that means... Fission!",
    "One neutron gets absorbed, but two more are released!",
    "Now let's take a look at the coolant.",
    "Each fission releases a little heat.",
    "Power plants can turn that heat into electricity,",
    "But first it needs to get out of the reactor.",
    "Coolant flows in and out of the reactor.",
    "It carries the heat away, so the fuel doesn't overheat.",
    "You want to place the coolant near the fuel",
    "So the heat gets removed quickly.",
    "You also want to make sure the coolant is big enough.",
    "Because it can only remove heat if it is still cold.",
    "On the right, you can find the coolant flow meter.",
    "To save money, the coolant slows down if it's not used.",
    "That will mean it can't remove as much heat.",
    "So you might need to turn it up when things start to get hot!",
    "Let's see this coolant in action.",
    "Did you see the heat go from the fuel into the coolant?",
    "Finally, let's take a look at the poison.",
    "In nuclear reactors, poison means neutron poison.",
    "Poison atoms are very sticky and very stable.",
    "So if a neutron crashes into them, it's absorbed.",
    "We want some of the neutrons are to be absorbed in the poison.",
    "If all the neutrons are absorbed by the fuel, ",
    "More and more neutrons will be released.",
    "Pretty soon, we lose control of them.",
    "Too many neutrons means too many fissions,",
    "The reactor will either blow up or melt down.",
    "(But these days all reactors are designed to never blow up.)",
    "We put a lot of poison in reactors.",
    "But we leave a way to take it out a little at time.",
    "That way, we can control how fast the neutrons multiply.",
    "If the number of neutrons isn't changing, we call that criticality.",
    "We like criticality. It means everything is under control.",
    "At the top of the screen, you can see the criticality measure.",
    "During the game, you want that number to be about 1.",
    "If the number of neutrons is growing, we call that supercriticality.",
    "If the criticality meter at the top of the screen gets above 1.2,",
    "You lose control of the neutrons, and it's game over.",
    "So you need to make sure to put a lot of poison in,",
    "But turn the insertion down to 0% (bottom right).",
    "Then insert the poison a little at a time to keep criticality at 1.",
    "For your convenience, poison insertion will start at 10%",
    "There are two more ways the game ends.",
    "Your fuel could overheat if there isn't enough coolant flow.",
    "Or you could run out of neutrons.",
    "Just reset neutrons to tweak your reactor design,",
    "Or reset gameboard (top right) to clear everything.",
    "You're almost ready to play!",
    "Just click and hold a button until your cursor is the size you want.",
    "Then click on the gameboard to place it!",
    "When you like your design, turn down the poison...",
    "And click start!",
]

poison_color = (
    max(0, 255 - (255 - 165) * poison_effectiveness),
    max(0, 255 - (255 - 42) * poison_effectiveness),
    max(0, 255 - (255 - 42) * poison_effectiveness),
)
while tutorial_step < len(tutorial_messages):
    tutorial_message = tutorial_messages[tutorial_step]
    repaint_gameboard(message=tutorial_message)
    if tutorial_message == "It bounces back into the reactor!" and len(neutrons) == 0:
        primary_birth()
    if (
        tutorial_message == "Surrounding the reflector, you can see there is shielding."
    ) and len(neutrons) > 0:
        death(0)

    if (
        tutorial_message == "Let's start with the moderator."
        and len(moderator_spots) == 0
    ):
        place_mod()
    if tutorial_message == "And they slow down the neutrons." and len(neutrons) == 0:
        primary_birth()
    if tutorial_message == "Now how about the fuel?" and len(fuel_spots) == 0:
        death(0)
        place_fuel()
    if (
        tutorial_message == "You know what that means... Fission!"
        and len(neutrons) == 0
    ):
        primary_birth()
    if tutorial_message == "Now let's take a look at the coolant.":
        for neutron in neutrons:
            death(0)
        coolant_spots.append(
            {
                "position": fist_coolant_pos,
                "size": place_here_size / 2,
                "at_capacity": 0,
            }
        )
    if tutorial_message == "Let's see this coolant in action." and len(neutrons) == 0:
        fuel_tutorial_step_is_passed = True
        primary_birth()
    if tutorial_message == "Finally, let's take a look at the poison.":
        reset_gameboard()
        poison_spots.append({"position": first_mod_pos, "size": place_here_size / 2})

    if tutorial_message == "So if a neutron crashes into them, it's absorbed.":
        iter += 1
        if iter == 5:
            primary_birth()
            iter = 0

    dt = clock.tick(60) / 1000
    advance_if_clicked()

with open("pool_table_game.py", "r") as file:
    python_code = file.read()
    exec(python_code)
