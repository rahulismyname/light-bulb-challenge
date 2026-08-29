# Light Bulb Challenge

Your goal for this tech task is to control a Light Bulb using Natural Language.

In `light_bulb.py`, you will find a `LightBulb` class, with methods `turn_on()`, `turn_off()` and `set_brightness()`.
These methods update the attributes of the `LightBulb` object, and print a statement that reflects the taken action.

Your task is to implement a CLI through which a user can send Natural Language commands to call the
methods of the `LightBulb`.

# Part 1: On & Off

The first step will be to switch the light on and off. An example of our terminal would be:

```bash
>>> User: Please turn the light on
Light Bulb switched ON

>>> User: Now please turn it off
Light Bulb switched OFF

>>> User: Switch it back on instead of off
Light Bulb switched ON
```

# Part 2 (Bonus): Set Brightness

The second step is more advanced. We want to pass a value to the `set_brightness()` function:

```bash
>>> User: Please set the brightness to 70%
Light Bulb brightness set to 70%

>>> User: Now set it to 10% instead of 70%
Light Bulb brightness set to 10%
```

# Notes:

- You are given full freedom of implementation for the application.
- You can use any tool at your disposal.
- Success on more advanced commands is highly valued. E.g:
    - *"Toggle the light"*: Takes current state into account and switches it
    - *"Reduce the brightness by 20%"*: Makes a relative change to the current brightness.
- Any effort to improve the application further is also highly valued (VCS, abstractions, containerization, testing, etc.)
- Please write any instructions or details of your solution in a `SOLUTION.md` file.

