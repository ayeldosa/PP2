# TSIS 2 – Paint Application

## Requirements
```
pip install pygame
```

## Run
```
python paint.py
```

## Controls

| Key / Action         | Effect                              |
|----------------------|-------------------------------------|
| Click toolbar button | Select tool                         |
| `1` / `2` / `3`     | Brush size: small / medium / large  |
| `Ctrl+S`             | Save canvas as timestamped PNG      |
| Click canvas         | Draw / use active tool              |
| **Text tool** – click canvas | Place text cursor            |
| Type characters      | Build text string (preview shown)   |
| `Enter`              | Commit text to canvas               |
| `Escape`             | Cancel text input                   |

## Tools

| Tool          | Description                                         |
|---------------|-----------------------------------------------------|
| Pencil        | Freehand drawing                                    |
| Line          | Straight line with live preview                     |
| Rectangle     | Drag to draw rectangle outline                      |
| Circle        | Drag to draw circle outline                         |
| Square        | Constrained rectangle (equal sides)                 |
| R.Triangle    | Right-angle triangle                                |
| Eq.Triangle   | Equilateral triangle                                |
| Rhombus       | Diamond shape                                       |
| Eraser        | Erase to white                                      |
| Fill          | Flood-fill enclosed region with active colour       |
| Text          | Click to place, type, Enter to confirm              |

## File structure
```
TSIS2/
├── paint.py    # main app + toolbar + event loop
└── tools.py    # all tool classes + geometry helpers
```
