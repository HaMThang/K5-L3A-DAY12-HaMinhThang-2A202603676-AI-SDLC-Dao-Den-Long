# Credits

Record every third-party or AI-generated asset used in the game.

| Asset | Creator/source | License or tool | Changes made |
|---|---|---|---|
| Procedural 3D environment, HUD, and effects | Created in this repository with Codex assistance | Original code; MIT project license | Generated from WebGL primitives |
| Archangel Artamiel character model + texture atlas | User-provided `light-archangel-artamiel.zip` bundle | No license file was included in the supplied bundle | OBJ/MTL/PNG copied to `src/assets/`; imported as a textured WebGL mesh, scaled to player height, with a straw conical hat added in-game |
| Firefly wisp sprite | OpenAI ImageGen, based on the user's reference image | AI-generated project asset | Recolored to amber and yellow, transparent background; saved as `src/assets/firefly-wisp.png` |

The project code is distributed under the MIT License in `LICENSE`. The environment is procedural; the player uses the model and texture supplied by the user in `light-archangel-artamiel.zip`. The firefly sprite was generated for this project from the user's reference. No external fonts or audio assets are used.
