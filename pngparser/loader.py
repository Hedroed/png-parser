class Loader():
    """
    Configurate and display colorful progress bar in terminal.

    Create a instance of Loader with current value and max value.
    Display the current position depending on the max value.
    Update the current position to increase the position.
    """

    def __init__(self, current: int=0, max: int=100):
        self.current = current
        self.max = max

        self.color1 = '\033[44m'
        self.color2 = '\033[46m'
        self.colorReset = '\033[0m'
        self.colorText = '\033[30m'

    def setCurrent(self, current: int):
        """Set the current progression.

        Args:
            current: the current progression of the bar. If current is greater
                than max, the ba stay at 100%
        """
        self.current = current

    def increase(self, val: int=1):
        """Increase the current progression.

        Args:
            val: the value to increase, default to 1. If current is greater
                than max, the ba stay at 100%

        """
        self.current += val

        if self.current > self.max:
            self.current = self.max

    def __addSpace(self, val, count=3):
        if val < 10:
            return ('  %.0f' % val)
        elif val < 100:
            return (' %.0f' % val)
        else:
            return ('%.0f' % val)

    def draw(self):
        """Draw the bar."""
        percentCurrent = int(self.current / self.max * 100)

        display = self.__addSpace(percentCurrent) + '%'
        pos = percentCurrent - min(4, percentCurrent)

        if percentCurrent == 0:
            display = ''
            pos = 0
        elif percentCurrent < 4:
            display = display[-percentCurrent:]

        print('\r' +
              self.color1 +
              self.colorText +
              (' ' * pos) +
              display +
              self.color2 +
              (' ' * (100 - percentCurrent)) +
              self.colorReset, end="")