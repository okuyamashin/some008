# 『鬼火の沼と古いランタン』画像プロンプト集

## 組み立て方

1枚のプロンプトは、次のブロックを上から順につなげて作ります。

```
[Style] + [Hero] + [Item] + [Tone] + [Scene] + [Composition] + [Frame]
```

- [Style] [Hero] [Frame] は全ページ共通です。一字一句変えずに使います。
- [Item] と [Tone] は、場面ごとに指定された方を選びます。[Item] は物語の途中で姿が変わる主人公の持ち物です。
- [Scene] と [Composition] は場面ごとに書き換えます。
- 表紙だけはカラーなので、[Style] の代わりに [Cover Style] を使います。
- 保存先は `books/onibi-no-numa/images/raw/<ファイル名>_v1.png` です。候補が複数あるときは `_v2`、`_v3` と番号を増やします。
- 下の表の Item 列が before / after で始まる場面に [Item: before] / [Item: after] を付けます（「なし」なら付けない）。

## 共通ブロック

### [Style]（表紙以外）

```text
[Style]
Black-and-white copperplate engraving, in the manner of 19th-century book illustrations such as Gustave Doré.
Fine-line cross-hatching and stippling, pure black ink on white paper.
Every tone, including mist, fog and beams of light, is rendered only with fine engraved lines and dots.
No color, no gray wash, no airbrushed or photographic shading, no soft gradients. High contrast.
No text, no letters, no signature, no frame or border.
```

### [Cover Style]（表紙のみ）

```text
[Cover Style]
A painted cover for a classic 1980s fantasy adventure gamebook paperback.
Rich color, gouache and oil painting look, dramatic lighting, heroic and serious mood.
No text, no letters, no title, no signature, no frame or border.
```

### [Hero]

```text
[Hero]
A young traveler, always seen from behind or in three-quarter rear view.
Face hidden in the shadow of a deep hood.
Long dark hooded cloak, simple leather armor, a small travel satchel.
```

### [Item]（どちらか1つ）

before は、物語の前半（姿が変わる前）で使います。

```text
[Item: before]
An old, sooty iron lantern with rusted frame and clouded glass, empty and unlit, hanging from the hero's belt.
```

after は、姿が変わった後と表紙で使います。

```text
[Item: after]
The same old iron lantern, now glowing brightly from within with a small will-o'-wisp flame, drawn as radiating engraved lines.
```

### [Tone]（どちらか1つ。表紙には付けない）

```text
[Tone: story]
Light and airy overall, with generous white areas.
```

```text
[Tone: bad ending]
Darker and denser, with deep shadows, drawn completely seriously like a tragic scene in an old book. Not cartoonish, not cute.
```

### [Frame]

```text
[Frame]
Vertical portrait composition for a book page.
Open white space around the edges so the image sits on the page like a printed vignette.
```

表紙だけは [Frame] の代わりに [Cover Frame] を使います。

```text
[Cover Frame]
Vertical portrait composition for a book cover, painted all the way to the edges with no white margin.
```

## 場面ごとのブロック

| ファイル名 | 場面 | Item | Tone | 状態 |
| --- | --- | --- | --- | --- |
| 00_cover | 表紙 | after | なし（Cover Style） | 未作成 |
| 01c_choice | 場面1：選択 | なし | story | 未作成 |
| 01r_result | 場面1：正解 | before | story | 未作成 |
| 01b_bad | 場面1：バッドエンド | なし | bad ending | 未作成 |
| 02c_choice | 場面2：選択 | before | story | 未作成 |
| 02r_result | 場面2：正解 | after（手に持つ） | story | 未作成 |
| 02b_bad | 場面2：バッドエンド | before | bad ending | 未作成 |
| 03c_choice | 場面3：選択 | after | story | 未作成 |
| 03r_result | 場面3：正解 | after | story | 未作成 |
| 03b_bad | 場面3：バッドエンド | after | bad ending | 未作成 |
| 04c_choice | 場面4：選択 | after | story | 未作成 |
| 04r_result | 場面4：正解 | after | story | 未作成 |
| 04b_bad | 場面4：バッドエンド | after | bad ending | 未作成 |
| 05c_choice | 場面5：選択 | after | story | 未作成 |
| 05r_ending | 場面5：正解（エンディング） | after | story | 未作成 |
| 05b_bad | 場面5：バッドエンド | after | bad ending | 未作成 |

### 00_cover　表紙

[Cover Style] + [Hero] + [Item: after] + 以下 + [Cover Frame]

```text
[Scene]
A misty marsh at night, dead trees and tall reeds, dozens of pale blue will-o'-wisps floating over black water.
On a stilt hut in the distance, a hunched old witch with a crooked staff is silhouetted against a green-glowing window, wisps circling her.
The hero stands small in the foreground on a stepping stone, holding up the glowing lantern.

[Composition]
The witch's hut and the swirling wisps fill the upper and middle part; the hero stands at the bottom center, seen from behind.
Keep the top quarter calm and dark so a title can be placed over it later.
```

### 01c_choice　場面1：選択

[Style] + [Hero] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A small village beside a misty marsh at dusk. Bundles of dried herbs hang over every doorway.
By a stone well, an old village elder leaning on a staff pleads with the hero, open-handed.
Beyond the rooftops, pale will-o'-wisps already drift over the marsh.

[Composition]
The elder by the well is at the center; the hero stands at the lower left, seen from behind; the wisps are small at the upper right.
```

### 01r_result　場面1：正解

[Style] + [Hero] + [Item: before] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Inside a humble cottage by the hearth.
The old elder holds out an old sooty iron lantern with clouded glass, empty, toward the hero.

[Composition]
The empty lantern between them is the visual center; the hero is at the lower left, seen in three-quarter rear view.
```

### 01b_bad　場面1：バッドエンド

[Style] + [Hero] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
Thirty years later, a village square completely swallowed by thick mist; only the nearest well and a few figures are visible.
The hero, older now, stands on a small wooden box, seen from behind, solemnly announcing the weather to a few villagers wrapped in shawls.
A small chalkboard on an easel beside the hero is blank except for a drawing of a cloud.

[Composition]
The hero on the box is at the lower left; the thick mist fills everything else.
```

### 02c_choice　場面2：選択

[Style] + [Hero] + [Item: before] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Deep in a misty marsh at dusk, with rotten reeds, dead trees and black pools.
A single pale will-o'-wisp floats a little way ahead, beckoning over what looks like a dry path.
The hero stands in the mire, the empty lantern at the belt.

[Composition]
The beckoning wisp is the visual center; the hero stands at the lower left, seen from behind.
```

### 02r_result　場面2：正解

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
In the misty marsh at night, the hero holds up the lantern, its lid closing; inside, a small wisp curls up like a sleeping cat, glowing brightly.
Its light reveals a line of stepping stones across the black water.

[Composition]
The glowing lantern is the visual center at the top; the stepping stones lead away from the hero at the lower left, seen in three-quarter rear view.
```

### 02b_bad　場面2：バッドエンド

[Style] + [Hero] + [Item: before] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
A muddy hollow in the marsh at night.
The hero, seen from behind, sits in the mud wearing a crown of reeds, solemnly conducting with a reed baton.
Dozens of frogs sit in rows on lily pads and logs, mouths wide open, singing.

[Composition]
The rows of singing frogs fill the upper two thirds; the hero conducting is at the lower left, seen from behind.
```

### 03c_choice　場面3：選択

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A hut on tall wooden stilts in the misty marsh, green light spilling from its window.
Two ways lead to it: an old plank bridge with a crooked signpost, boards blackened, over strangely still water; and a line of stepping stones lit by the lantern.
The hero stands at the parting of the ways, lantern held up.

[Composition]
The stilt hut is at the top center; the plank bridge runs in from the left, the stepping stones from the right; the hero is at the bottom center, seen from behind.
```

### 03r_result　場面3：正解

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
At the foot of the stilt hut, the hero stands on the last stepping stone, looking back.
Behind, the plank bridge is collapsing and sinking into the mud with nobody on it.
A rope ladder hangs down from the hut's door.

[Composition]
The sinking bridge is at the left; the hero is at the lower right, seen in three-quarter rear view; the rope ladder rises at the top right.
```

### 03b_bad　場面3：バッドエンド

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
The marsh in spring. The hero is sunk in mud up to the neck, seen from behind, only the hooded head above the mire.
A tall heron stands on the hero's head beside a nest with three chicks.
In the background, well-dressed townsfolk with parasols have come to look.

[Composition]
The hooded head with the heron and nest is the visual center at the bottom; the onlookers are small at the upper right.
```

### 04c_choice　場面4：選択

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Inside the witch's cosy hut: a crackling hearth, shelves crowded with dried herbs and jars.
Before the hearth stands a deep, soft armchair with a small card hanging from it; its arms are covered in scratch marks.
The hero stands nearby; the wisp in the lantern has shrunk small. A stair at the back leads up toward a green glow.

[Composition]
The armchair is the visual center; the hero is at the lower left, seen from behind; the stair is at the upper right.
```

### 04r_result　場面4：正解

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
The hero climbs a narrow wooden stair, seen from behind, lantern blazing bright.
Below, the armchair's arms have closed together on nothing, as if disappointed.
At the top of the stair, a door with green light glowing around its edges.

[Composition]
The stair rises from the lower left to the door at the upper right; the hero is in the middle; the chair is small at the bottom.
```

### 04b_bad　場面4：バッドエンド

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
The witch's hut at night by the hearth.
The hero sits trapped in the armchair, whose arms clasp the hero tight, seen from behind; both hands hold out a skein of yarn.
Beside the chair, a hunched old witch in a shawl knits contentedly; behind her, a towering pile of knitted socks.

[Composition]
The pile of socks rises at the right; the witch knits at the center; the trapped hero is at the lower left, seen from behind.
```

### 05c_choice　場面5：選択

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
The witch's chamber at the top of the stilt hut, lit green.
A great cauldron bubbles in the center; before it stands a crook-backed old witch with a crooked staff.
Scores of wisps circle around her, casting her shadow huge across the walls.
The hero stands in the doorway, the lantern glowing at the side.

[Composition]
The witch and her huge shadow fill the upper two thirds; the hero is small at the bottom center, seen from behind.
```

### 05r_ending　場面5：正解（エンディング）

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Night in the village square, mist gone and stars out.
The wisp lantern hangs high on a post as a street lamp, many wisps glowing inside it.
Villagers welcome back cattle, sheep and two young people; at the edge of the square, a grumpy little old woman sweeps the step of a herb shop.

[Composition]
The lantern street lamp is at the top center; the happy villagers fill the middle; the hero is at the lower left, seen in three-quarter rear view.
```

### 05b_bad　場面5：バッドエンド

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
The witch's green-lit chamber.
The hero, seen from behind, wears a witch's apron and stirs the great cauldron; small wisps rise from it.
One wisp floats off carrying a tiny rolled-up map in a little ribbon.
The old witch naps in a rocking chair nearby.

[Composition]
The cauldron and rising wisps are the visual center; the hero is at the lower left, seen from behind; the napping witch is at the right.
```
