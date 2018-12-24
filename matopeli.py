import msvcrt
import time

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

def win_get_direction(timeout):
	start = time.time()
	key = None
	while True:
		time.sleep(0.01)
		if msvcrt.kbhit():
			if msvcrt.getch() == b'\xe0':
				key = {
					b'H': UP,
					b'P': DOWN,
					b'K': LEFT,
					b'M': RIGHT,
				}[msvcrt.getch()]
		if time.time() - start > timeout:
			break
	return key

def direction_to_text(direction):
	return {
		0: "up",
		1: "down",
		2: "left",
		3: "right",
	}[direction]

def legal_direction(previous, next):
	if previous == next:
		return False
	else:
		return {
			UP: DOWN,
			DOWN: UP,
			LEFT: RIGHT,
			RIGHT: LEFT,
		}[previous] != next

def move(pos, direction, n):
	if direction == UP:
		pos[1] -= n
	elif direction == DOWN:
		pos[1] += n
	elif direction == LEFT:
		pos[0] -= n
	elif direction == RIGHT:
		pos[0] += n

class Game:
	def __init__(self, size=(100, 100)):
		self.size_x = size[0]
		self.size_y = size[1]
		self.mato = None
		self.food = None

	def __repr__(self):
		grid = [[None for _ in range(self.size_x + 1)] for _ in range(self.size_y + 1)]
		grid[0] = ["-" for _ in range(self.size_x + 2)]
		grid[-1] = ["-" for _ in range(self.size_x + 2)]
		for row in range(self.size_y):
			grid[row + 1][0] = '|'
			grid[row + 1][-1] = '|'
		
		for part in self.mato.parts:
			pos = list(part.start)
			grid[pos[1] + 1][pos[0] + 1] = "■"
			for _ in range(part.length):
				move(pos, part.direction, 1)
				grid[pos[1] + 1][pos[0] + 1] = "■"
		return '\n'.join(''.join(s or " " for s in r) for r in grid)

class Part:
	def __init__(self, start, direction, length):
		self.start = start
		self.direction = direction
		self.length = length

	def move(self, head=False, tail=False):
		if head:
			self.length += 1
		elif tail:
			self.length -= 1
			move(self.start, self.direction, 1)

	def get_head(self):
		out = list(self.start)
		move(out, self.direction, self.length)
		return out

	def covers(self, position):
		direction = -1 if self.direction in [LEFT, UP] else 1
		pos = list(self.start)
		if pos == position:
			return True
		for _ in range(self.length):
			move(pos, self.direction, direction)
			if pos == position:
				return True

	def __repr__(self):
		start = self.start
		direction = direction_to_text(self.direction)
		length = self.length
		return f"Part<start={start} direction={direction} length={length}>"

class Mato:
	def __init__(self, parts=None):
		self.parts = parts or []
		self.next_direction = None

	def move(self):
		if self.next_direction is not None:
			self.add_part()
		self.parts[-1].move(head=True)
		self.parts[0].move(tail=True)
		if self.parts[0].length < 1:
			del self.parts[0]

	def add_part(self):
		legal = legal_direction(self.parts[-1].direction, self.next_direction)
		if not legal:
			direction = direction_to_text(self.next_direction)
			print(f"illegal direction: {direction}")
		else:
			start = list(self.parts[-1].get_head())
			direction = self.next_direction
			length = 0
			self.parts.append(Part(start, direction, length))
		self.next_direction = None

	def covers(self, position):
		for part in self.parts[:-1]:
			if part.covers(position):
				return True

	def __repr__(self):
		return '\n'.join(str(p) for p in self.parts)

def main():
	game = Game(size=(30, 30))
	mato = Mato()
	game.mato = mato
	mato.parts = [
		Part([0, 0], RIGHT, 7),
	]
	while True:
		mato.next_direction = win_get_direction(0.1)
		mato.move()
		print(mato)
		print(game)
		if mato.covers(mato.parts[-1].get_head()):
			print("hävisit pelin")
			break

if __name__ == "__main__":
	main()
