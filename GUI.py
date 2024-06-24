import pygame

class GUI:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((400, 400), pygame.RESIZABLE)
        pygame.display.set_caption('Premier League Football Manager')
        
        # Load the image
        self.textTitleImage = pygame.image.load('football_manager.png').convert_alpha()
        
        # Initialize scaled image and position
        self.scaledImage = self.textTitleImage
        self.imagePosition = (0, 0)

        self.running = True
        self.mainLoop()

    def updateImageSize(self, image, oldWindowSize, newWindowSize):
        imageWidth, imageHeight = image.get_size()
        oldWindowWidth, oldWindowHeight = oldWindowSize
        newWindowWidth, newWindowHeight = newWindowSize

        # Calculate scale factors for width and height based on old and new window dimensions
        scaleX = newWindowWidth / oldWindowWidth
        scaleY = newWindowHeight / oldWindowHeight

        # Scale the image
        scaledImage = pygame.transform.smoothscale(image, 
                                                   (int(imageWidth * scaleX), int(imageHeight * scaleY)))

        return scaledImage

    def mainLoop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    newWindowSize = (event.w, event.h)
                    self.handleResize(newWindowSize)

            self.window.fill((255, 255, 255))  # Fill window with white color

            # Update image size based on current and previous window size
            currentWindowSize = self.window.get_size()
            self.scaledImage = self.updateImageSize(self.textTitleImage, currentWindowSize, currentWindowSize)

            # Calculate image position to center it horizontally and at the top
            imageWidth, imageHeight = self.scaledImage.get_size()
            self.imagePosition = ((currentWindowSize[0] - imageWidth) // 2, 0)  # Centered horizontally, at the top

            # Blit the scaled image onto the window
            self.window.blit(self.scaledImage, self.imagePosition)

            pygame.display.flip()

    def handleResize(self, newWindowSize):
        self.window = pygame.display.set_mode(newWindowSize, pygame.RESIZABLE)


