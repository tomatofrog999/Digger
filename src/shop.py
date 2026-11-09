import pygame
import game_essential as game
import os
import sys
import game_ui as ui
import pygwidgets

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.dirname(CURRENT_PATH)
ASSET_PATH = os.path.join(BASE_PATH, "assets")
IMAGE_PATH = os.path.join(ASSET_PATH, "images")
FONT_PATH = os.path.join(ASSET_PATH, "fonts")

pygame.init()

FULLSCREEN = False
screeninfo = pygame.display.Info()
ORIGINAL_SCREEN_WIDTH = 800
ORIGINAL_SCREEN_HEIGHT = 600
SCREEN_WIDTH = screeninfo.current_w if FULLSCREEN else ORIGINAL_SCREEN_WIDTH
SCREEN_HEIGHT = screeninfo.current_h if FULLSCREEN else ORIGINAL_SCREEN_HEIGHT

#UP3_X = 313
#UP4_X = 540




BUTTON_SCALE = SCREEN_WIDTH/SCREEN_HEIGHT * 4 if FULLSCREEN else 4


def main_menu():
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    clock = pygame.time.Clock()
        
    exit_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "leave.png"), True)
    exit_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "leave_over.png"), True)
    up1_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "up1.png"), True)
    up1_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "up1_over.png"), True)
    up2_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "up2.png"), True)
    up2_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "up2_over.png"), True)
    dealer_surf = game.load_picture(os.path.join(IMAGE_PATH, "dealer.png"), True)
    border1_surf = game.load_picture(os.path.join(IMAGE_PATH, "border1.png"), True)
    border1_surf = pygame.transform.scale(border1_surf, ((border1_surf.get_width()*6, border1_surf.get_height()*9.85)))
    energy_surf = game.load_picture(os.path.join(IMAGE_PATH, "energy.png"), True)
    energy_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "energy_over.png"), True)
    stash_surf = game.load_picture(os.path.join(IMAGE_PATH, "stash.png"), True)
    stash_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "stash_over.png"), True)
                                                
    leave_button = ui.ScalableButton(screen, (round(LEAVE_X), round(LEAVE_Y)), exit_up_surf, exit_over_surf, BUTTON_SCALE, "bottomright")
    up1_button = ui.ScalableButton(screen, (round(UP_X), round(UP_Y)), up1_up_surf, up1_over_surf, 6, "topleft")
    up2_button = ui.ScalableButton(screen, (round(UP2_X), round(UP_Y)), up2_up_surf, up2_over_surf, 6, "topleft")
    stash_button = ui.ScalableButton(screen, (round(UP_X), round(171)), stash_surf, stash_over_surf, 6, "topleft")
    energy_button = ui.ScalableButton(screen, (round(43), round(302)), energy_surf, energy_over_surf, 6, "topleft")

    #up3_button = ui.Button(screen, (round(UP3_X), round(UP_Y)), up1_up_surf, up1_over_surf, 6, "topleft")
    #up4_button = ui.Button(screen, (round(UP4_X), round(UP_Y)), up2_up_surf, up2_over_surf, 6, "topright")

    dealer = ui.ScalableButton(screen, (775, 25), dealer_surf, dealer_surf, 8.5, "topright")
    border1 = ui.ScalableButton(screen, (25,25), border1_surf, border1_surf, 1, "topleft")
    border2 = ui.ScalableButton(screen, (525,25), border1_surf, border1_surf, 1, "topleft", flip_x= True)

    up1_info_text = "Copper Shovel\n--------------------\n+1 Break Damage"
    up2_info_text = "Netherite Shovel\n--------------------\n+2 Break Damage"
    stash_info_text = "BF Bag\n--------------------\n+50 Bag Slot"
    energy_info_text = "Monsta Energy\n--------------------\n+50 Max Energy"

    up1_info = pygwidgets.DisplayText(screen, (598,250), up1_info_text, os.path.join(FONT_PATH, "Silkscreen-Regular.ttf"), fontSize = 15, width = 177, height = 250 , textColor = "white", backgroundColor = "#252525")
    up2_info = pygwidgets.DisplayText(screen, (598,250), up2_info_text, os.path.join(FONT_PATH, "Silkscreen-Regular.ttf"), fontSize = 15, width = 177, height = 250 , textColor = "white", backgroundColor = "#252525")
    stash_info = pygwidgets.DisplayText(screen, (598,250), stash_info_text, os.path.join(FONT_PATH, "Silkscreen-Regular.ttf"), fontSize = 15, width = 177, height = 250 , textColor = "white", backgroundColor = "#252525")
    energy_info = pygwidgets.DisplayText(screen, (598,250), energy_info_text, os.path.join(FONT_PATH, "Silkscreen-Regular.ttf"), fontSize = 15, width = 177, height = 250 , textColor = "white", backgroundColor = "#252525")
            
    shop_group = ui.UIGroup([leave_button, up1_button, up2_button, dealer, border1, border2, stash_button, energy_button])
    
    running = True
    
    while running:
        
        events = pygame.event.get()

        mouse_pos = pygame.mouse.get_pos()

        clicked = shop_group.update(mouse_pos, events)
        
        screen.fill("#000000")
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.QUIT:
                running = False
        
        if clicked[0]:
            self.scene_manager.stop

        if up1_button.activated:
            up1_info.draw()
            if up1_button.clicked:
                pass
        
        if up2_button.activated:
            up2_info.draw()
            if up2_button.clicked:
                pass
        
        if stash_button.activated:
            stash_info.draw()
            if stash_button.clicked:
                pass
        
        if energy_button.activated:
            energy_info.draw()
            if energy_button.clicked:
                pass
        

        
        shop_group.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


main_menu()


