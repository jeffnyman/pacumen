<h1 align="center">
    <img src="https://github.com/jeffnyman/pacumen/blob/master/images/pacumen-title-bw-55.png" alt="Pacumen">
    <img src="https://github.com/jeffnyman/pacumen/blob/master/images/pacumen-game.png" alt="Pac-Man Game Board">
</h1>

<h3 align="center">Exploring Artificial Intelligence with Pac-Man</h3>

---

> "We do not wish to penalise the machine for its inability to shine in beauty competitions, nor to penalise a man for losing in a race against an aeroplane."<br>
> &nbsp;&nbsp;&nbsp;&nbsp;**Alan Turing, 1950, _Computing Machinery and Intelligence_**

---

> "The quest for 'artificial flight' succeeded when the Wright brothers and others stopped imitating birds and started learning about aerodynamics."<br>
> &nbsp;&nbsp;&nbsp;&nbsp;**Stuart Russell & Peter Norvig, 1994, _Artificial Intelligence: A Modern Approach_**

---

The name of this project is based on the name "Pac-Man" and the word "acumen." The latter term generally refers to the ability to make good judgments and quick decisions. This is often done in a particular domain. That domain, for this project, will be in the context of a simplified Pac-Man game.

The goal of Pacumen is to provide an application that will allow for testing out aspects of machine learning and artificial intelligence, like algorithmic searching as well as more advanced concepts like reinforcement learning. This is an environment that can easily map onto the general definitions of search problems and decision processes. These are what characterize most approaches to artificial intelligence.

**Pacumen** is an implementation of the [Pacman AI project](http://ai.berkeley.edu) developed at UC Berkeley. In terms of the Berkeley AI code, Pacumen is a very substantial change. The most notable is that Pacumen only runs under Python 3. Internally, there are a lot of changes as well, in terms of making the code more modular, maintainable and scalable as well as more idiomatic to Python. Also removed were certain code elements that had to do with student grading and contests.

# Running Pacumen

In all cases, I'll show commands as `python3` and `pip3` for those operating systems that make the distinction. If you are on a system where only Python 3 is installed, you can replace those with `python` and `pip`, respectively.

## Basic Usage

As a Python module, in the project root, you can run this command:

    python3 -m pacumen

## Installing Pacumen

You can use the [pip package manager](https://pip.pypa.io/) to install the application. In the project root, do this:

```
pip3 install .
```

By default, pip will install Python packages to a system directory. You can have pip install packages in your home directory instead, as such:

```
python3 -m pip install --user .
``` 
    
With either approach the application is then available as a distinct application that can be called from anywhere on your file system.

After install via pip, you can do this:

```
pacumen
```

## Concepts

A key question is this: can a computer learn from experience? Here, past experiences are called data. Researchers are interested in algorithms that allow a computer to learn from data. If a computer program improves upon a certain task based on a past experience, then we can say that it has learned.

Machine learning is a field that discovers the structures of algorithms that enable all of this learning from data. These algorithms build a model that accepts inputs, and based on these inputs, the algorithms make predictions or results. We often can't provide all the preconditions in the program; so the algorithms, in those cases, are designed in such a way that they can learn based on feedback from the environment they are operating in.

The focus of Pacumen will be Pac-Man agents making decisions (taking actions) in a maze-like environment that provides the agent with rewards.

## Pacumen Implementation

A standard Pac-Man game consists of objects moving around on a set of squares that can be modeled as a grid. At any given time Pac-Man occupies a single square and faces one of the four directions: north, south, east, or west. There may be walls in between the square or entire squares might be blocked by walls.

In terms of adherence to the original Pac-Man game, Pacumen is a very simplified representation. There are dots (food pellets) and capsules (power pellets). The Pacumen agent can eat the power pellets and that will cause any ghosts on the board to become "scared." When the ghosts are scared, Pacumen can eat them. When that happens, the ghosts will immediately respawn at their starting location. Pacumen wins the game if he eats all of the dots on a given board.

Note that there are no "levels" in Pacumen. The goal is to try out machine learning algorithms in _episodes_, which are the duration state from when the game starts to when the game ends, either in a win or a loss.

As far as scoring, Pacumen gains 10 points for every food pellet he eats. Eating power pellets does not gain any points but if Pacumen eats a scared ghost, he gains 200 points. When the game is won (all dots eaten), Pacumen gains 500 points. However, if the game is lost -- meaning, Pacumen is eaten by a ghost -- then he loses 500 points. Finally, there is a "living reward" which is, in fact, a negative reward (thus a punishment). For every time step that Pacumen is in the game world, he loses 1 point.
