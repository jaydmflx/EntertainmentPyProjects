import turtle
import random
import time

# --- SCREEN SETUP ---
s = turtle.Screen()
s.setup(width=800, height=450)
s.bgcolor("#120F1C")  # Dark Arcade Aesthetic
s.title("Chrome Dino Run Arcade")
s.tracer(0)

# Constants
G = -140  # Ground baseline

# --- DECORATIVE GROUND & CLOUDS ---
ground_line = turtle.Turtle()
ground_line.hideturtle()
ground_line.penup()
ground_line.color("#4A3F6B")
ground_line.goto(-400, G)
ground_line.pendown()
ground_line.pensize(2)
ground_line.goto(400, G)

# Ground Texture Dots
ground_dots = []
for _ in range(15):
    dot = turtle.Turtle("square")
    dot.color("#2A2440")
    dot.shapesize(0.1, random.choice([0.2, 0.4, 0.6]))
    dot.penup()
    dot.goto(random.randint(-400, 400), G - random.randint(5, 25))
    ground_dots.append(dot)

# Background Clouds
clouds = []
for _ in range(3):
    cloud = turtle.Turtle("circle")
    cloud.color("#2A2440")
    cloud.shapesize(0.6, 1.8)
    cloud.penup()
    cloud.goto(random.randint(-350, 350), random.randint(40, 150))
    clouds.append(cloud)

# --- CHROME DINO COMPOSITE PARTS ---
COLOR_DINO = "#F5F5F0"
COLOR_EYE = "#120F1C"

dino_body = turtle.Turtle("square")
dino_body.color(COLOR_DINO)
dino_body.penup()

dino_snout = turtle.Turtle("square")
dino_snout.color(COLOR_DINO)
dino_snout.penup()

dino_eye = turtle.Turtle("square")
dino_eye.color(COLOR_EYE)
dino_eye.shapesize(0.2, 0.2)
dino_eye.penup()

dino_tail = turtle.Turtle("square")
dino_tail.color(COLOR_DINO)
dino_tail.shapesize(0.4, 0.6)
dino_tail.penup()

dino_arm = turtle.Turtle("square")
dino_arm.color(COLOR_DINO)
dino_arm.shapesize(0.2, 0.5)
dino_arm.penup()

leg_left = turtle.Turtle("square")
leg_left.color(COLOR_DINO)
leg_left.shapesize(0.6, 0.25)
leg_left.penup()

leg_right = turtle.Turtle("square")
leg_right.color(COLOR_DINO)
leg_right.shapesize(0.6, 0.25)
leg_right.penup()

# --- OBSTACLES (CACTI & PTERODACTYLS) ---
cacti = []
for _ in range(3):
    c = turtle.Turtle("square")
    c.color("#9370DB")  # Medium Purple Cacti
    c.shapesize(1.8, 0.5)
    c.penup()
    c.goto(1000, G + 18)
    cacti.append(c)

# Flying Pterodactyl
ptch = turtle.Turtle("triangle")
ptch.color("#FF69B4")  # HotPink Flying Enemy
ptch.shapesize(0.8, 1.4)
ptch.penup()
ptch.setheading(180)
ptch.goto(1500, G + 55)

# UI Text & Dust Particles
particles = []
text = turtle.Turtle()
text.hideturtle()
text.penup()

score = 0
high_score = 0
speed = 7
v = 0
ducking = False
playing = True

# --- INPUT CONTROLS ---
def jump():
    global v
    if dino_body.ycor() <= G + 24 and not ducking:
        v = 13

def start_duck():
    global ducking
    if dino_body.ycor() <= G + 24:
        ducking = True

def stop_duck():
    global ducking
    ducking = False

def restart_game():
    if not playing:
        start_game()

def add_dust(x, y):
    p = turtle.Turtle("circle")
    p.color("#4A3F6B")
    p.shapesize(0.2, 0.2)
    p.penup()
    p.goto(x + random.randint(-4, 4), y)
    particles.append({"t": p, "life": 8, "dx": random.uniform(-2, -0.5)})

# --- RENDER CLASSIC CHROME DINO ---
def draw_dino(x, y, is_ducking, frame, is_airborne):
    if is_ducking and not is_airborne:
        # Crawling/Ducking Dino Silhouette
        dino_body.shapesize(0.7, 1.8)
        dino_body.goto(x, y - 4)
        
        dino_snout.shapesize(0.5, 0.8)
        dino_snout.goto(x + 22, y - 2)
        
        dino_eye.goto(x + 23, y + 1)
        dino_tail.goto(x - 22, y - 2)
        dino_arm.goto(x + 6, y - 8)
        
        # Alternating Legs (Ducking Run)
        if (frame // 4) % 2 == 0:
            leg_left.goto(x - 8, y - 14)
            leg_right.goto(x + 8, y - 12)
        else:
            leg_left.goto(x - 8, y - 12)
            leg_right.goto(x + 8, y - 14)
    else:
        # Standard Upright T-Rex Silhouette
        dino_body.shapesize(1.5, 0.9)
        dino_body.goto(x, y + 4)
        
        dino_snout.shapesize(0.7, 1.1)
        dino_snout.goto(x + 8, y + 21)
        
        dino_eye.goto(x + 11, y + 24)
        dino_tail.goto(x - 12, y - 2)
        dino_arm.goto(x + 10, y + 6)
        
        # Running Legs
        if is_airborne:
            leg_left.goto(x - 4, y - 12)
            leg_right.goto(x + 4, y - 12)
        else:
            if (frame // 4) % 2 == 0:
                leg_left.goto(x - 4, y - 14)
                leg_right.goto(x + 4, y - 10)
            else:
                leg_left.goto(x - 4, y - 10)
                leg_right.goto(x + 4, y - 14)

# --- MAIN GAME ROUTINE ---
def start_game():
    global score, high_score, speed, v, playing, ducking
    
    score = 0
    speed = 7
    v = 0
    ducking = False
    playing = True
    
    dino_x = -280
    dino_y = G + 20
    
    cacti_positions = [500, 850, 1200]
    for i, c in enumerate(cacti):
        c.goto(cacti_positions[i], G + 18)
        
    ptch.goto(1600, G + random.choice([35, 65]))
    text.clear()

    anim_frame = 0

    while playing:
        anim_frame += 1

        # 1. Gravity & Physics
        dino_y += v
        if dino_y > G + 20:
            v -= 0.95
        else:
            if dino_y < G + 20 and v < 0:
                add_dust(dino_x, G + 2)
            dino_y = G + 20
            v = 0   

        if ducking and dino_y > G + 20:
            v -= 1.6  # Quick drop command

        is_air = dino_y > G + 20
        draw_dino(dino_x, dino_y, ducking, anim_frame, is_air)

        # 2. Scroll Environment (Ground & Clouds)
        for dot in ground_dots:
            dot.setx(dot.xcor() - speed)
            if dot.xcor() < -400:
                dot.setx(400)

        for cl in clouds:
            cl.setx(cl.xcor() - 1)
            if cl.xcor() < -420:
                cl.goto(420, random.randint(40, 150))

        # 3. Cacti Obstacles Update
        for c in cacti:
            c.setx(c.xcor() - speed)
            
            if c.xcor() < -420:
                c.setx(random.randint(400, 650))
                c.shapesize(random.choice([1.5, 1.9, 2.3]), random.choice([0.4, 0.6]))
                score += 1
                if score > high_score:
                    high_score = score
                if score % 6 == 0:
                    speed += 0.8
                
            # Collision Check
            dino_hitbox_y = dino_y if not ducking else dino_y - 8
            if abs(dino_x - c.xcor()) < 22 and abs(dino_hitbox_y - c.ycor()) < 24:
                playing = False

        # 4. Pterodactyl Enemy Update
        ptch.setx(ptch.xcor() - (speed + 1.5))
        ptch.shapesize(0.5 if (anim_frame // 8) % 2 == 0 else 0.9, 1.4)  # Flap wings

        if ptch.xcor() < -420:
            ptch.goto(random.randint(650, 1050), G + random.choice([32, 65]))
            score += 1

        # Collision Check vs Pterodactyl
        dino_hitbox_y = dino_y + 6 if not ducking else dino_y - 6
        if abs(dino_x - ptch.xcor()) < 24 and abs(dino_hitbox_y - ptch.ycor()) < 18:
            playing = False

        # 5. Particle Effects
        for p in particles[:]:
            p["t"].setx(p["t"].xcor() + p["dx"])
            p["life"] -= 1
            if p["life"] <= 0:
                p["t"].goto(1000, 1000)
                particles.remove(p)

        # 6. Render Micro HUD
        text.clear()
        text.color("#FFD700")
        text.goto(160, 160)
        text.write(f"SCORE: {score:04d}   HI: {high_score:04d}", font=("Courier", 12, "bold"))
        
        s.update()
        time.sleep(0.012)

    # --- GAME OVER SCREEN ---
    text.goto(0, 30)
    text.color("#FF1493")
    text.write("GAME OVER", align="center", font=("Courier", 22, "bold"))
    
    text.goto(0, -5)
    text.color("#E0D2F0")
    text.write(f"FINAL SCORE: {score:04d}  |  HI-SCORE: {high_score:04d}", align="center", font=("Courier", 11, "bold"))
    
    text.goto(0, -40)
    text.write("PRESS 'R' TO RESTART", align="center", font=("Courier", 11, "normal"))
    s.update()

# --- KEYBOARD BINDINGS ---
s.listen()
s.onkeypress(jump, "space")
s.onkeypress(jump, "Up")
s.onkeypress(start_duck, "Down")
s.onkeyrelease(stop_duck, "Down")
s.onkeypress(start_duck, "s")
s.onkeyrelease(stop_duck, "s")
s.onkeypress(restart_game, "r")

# Start Game Loop
start_game()
turtle.done()