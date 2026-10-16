# 『囁きの森と月の角笛』画像プロンプト集

## 組み立て方

1枚のプロンプトは、次のブロックを上から順につなげて作ります。

```
[Style] + [Hero] + [Item] + [Tone] + [Scene] + [Composition] + [Frame]
```

- [Style] [Hero] [Frame] は全ページ共通です。一字一句変えずに使います。
- [Item] と [Tone] は、場面ごとに指定された方を選びます。[Item] は物語の途中で姿が変わる主人公の持ち物です。
- [Scene] と [Composition] は場面ごとに書き換えます。
- 表紙だけはカラーなので、[Style] の代わりに [Cover Style] を使います。
- 保存先は `books/sasayaki-no-mori/images/raw/<ファイル名>_v1.png` です。候補が複数あるときは `_v2`、`_v3` と番号を増やします。
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
An old hunting horn carved from an animal horn, with a long crack running down its middle, hanging from a cord at the hero's side.
```

after は、姿が変わった後と表紙で使います。

```text
[Item: after]
The same carved hunting horn, its crack now sealed by a seam of shining silver, glowing faintly with moonlight, hanging from a cord at the hero's side.
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
A deep, ancient forest at night, lit by a full moon through the trees.
On a great rock in a moonlit clearing stands an enormous grey wolf, the King of Wolves, with golden eyes, his pack gathered in the shadows below.
The hero stands small in the foreground, raising the glowing moon horn toward the wolf king.

[Composition]
The wolf king fills the upper and middle part; the hero stands at the bottom center, seen from behind.
Keep the top quarter calm and dark so a title can be placed over it later.
```

### 01c_choice　場面1：選択

[Style] + [Hero] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A small village at the edge of a deep, dark forest, at dusk. Doors are shut and boards are nailed across the windows.
A bent old village elder with a long beard and a staff stops the hero in the street, pleading with open hands.
Behind them, the tall trees of the forest loom over the rooftops.

[Composition]
The elder is at the center; the hero stands at the lower left, seen from behind; the dark forest rises at the top.
```

### 01r_result　場面1：正解

[Style] + [Hero] + [Item: before] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Inside a humble cottage lit by a hearth fire.
The old elder lifts an old carved hunting horn with a long crack down its middle out of a wooden chest and holds it out to the hero.

[Composition]
The cracked horn between the two is the visual center; the hero is at the lower left, seen in three-quarter rear view.
```

### 01b_bad　場面1：バッドエンド

[Style] + [Hero] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
Twenty years later, at night, at the edge of the village facing the dark forest.
The hero, older now, stands on a small hill with a lantern, singing toward the forest with arms open, seen from behind.
In the forest, many pairs of wolf eyes glow sleepily among the trees, and some wolves are curled up asleep.
Villagers peek out of their windows, nightcaps on.

[Composition]
The hero on the hill is at the lower left; the sleepy wolf eyes fill the forest in the upper half.
```

### 02c_choice　場面2：選択

[Style] + [Hero] + [Item: before] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Inside a deep, ancient forest with twisted branches knotted overhead.
The path forks: the broad right-hand path is easy and inviting; at the end of the narrow left-hand path, a small spring glows with moonlight-like light in daytime.
Faint wisps curl around the trees like whispering voices, drawn as fine engraved lines.
The hero stands at the fork, looking from one path to the other.

[Composition]
The fork is at the center; the hero stands at the bottom center, seen from behind; the glowing spring is small at the upper left.
```

### 02r_result　場面2：正解

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A small spring in a forest clearing, its water shining white like melted moonlight.
The hero kneels at the edge and lifts the horn from the water; light streams along the silver seam where the crack has closed.

[Composition]
The glowing horn and spring are the visual center; the hero kneels at the lower left, seen in three-quarter rear view.
```

### 02b_bad　場面2：バッドエンド

[Style] + [Hero] + [Item: before] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
A dim, tangled part of the forest around a large old tree stump.
The hero, a year later, hides behind a tree, cupping a hand to whisper toward a lost traveler with a backpack who is walking in circles around the stump.
Footprints form a deep worn circle around the stump.

[Composition]
The stump and its circle of footprints are at the center; the hiding hero is at the lower left, seen from behind.
```

### 03c_choice　場面3：選択

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Deep in the forest, a huge fallen tree spans the path like an arch.
Beneath it sit two grey wolf sentinels, ears up, fangs showing, rising to their feet.
Loose stones lie scattered on the path.
The hero stands before them, hand near the horn at the side.

[Composition]
The two wolves under the fallen-tree arch are the visual center; the hero is at the lower left, seen from behind.
```

### 03r_result　場面3：正解

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
The fallen-tree arch in the deep forest.
The two grey wolves walk ahead calmly, leading the hero through under the arch; one looks back over its shoulder.
The hero follows, holding the glowing horn.

[Composition]
The path under the arch recedes toward the center; the wolves are in the middle; the hero is in the foreground, seen from behind.
```

### 03b_bad　場面3：バッドエンド

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
A forest clearing in late afternoon.
The hero, seen from behind, is in mid-throw of a stone, arm raised.
A whole pack of wolves waits eagerly with wagging tails, several of them holding stones in their mouths, a pile of returned stones at the hero's feet.

[Composition]
The eager pack fills the right half; the hero throwing is at the lower left, seen from behind.
```

### 04c_choice　場面4：選択

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A mossy glade deep in a valley of the forest.
Little folk in pointed caps sit in a ring around a feast: a nut pie, honey cakes, a steaming pot of mushroom soup.
One little man holds out a brimming bowl of soup to the hero.
The little folk cast no shadows; at the edge of the glade, two wolves stand back, heads low.

[Composition]
The feast ring is the visual center; the hero stands at the lower left, seen from behind; the wary wolves are small at the upper right.
```

### 04r_result　場面4：正解

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
The same mossy glade, now empty: only a ring of white mushrooms, a mossy stump and a heap of pine cones remain.
The two wolves bound up to the hero happily.
Further down the valley, a long path leads toward a moonlit opening.

[Composition]
The mushroom ring is in the middle; the hero is at the lower left, seen in three-quarter rear view; the moonlit opening is at the top.
```

### 04b_bad　場面4：バッドエンド

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
A tiny scene among mushrooms at night: the hero, shrunk to the size of the little folk, stands at a washtub made from an acorn cup, washing dishes.
Behind, a towering pile of tiny dishes reaches up into the dark, while little folk dance at a feast in the background.

[Composition]
The towering pile of dishes is the visual center; the tiny hero at the washtub is at the lower left, seen from behind.
```

### 05c_choice　場面5：選択

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A quiet moonlit glade deep in the valley.
On a great rock in its center sits an enormous grey wolf, the King of Wolves, with golden eyes full of sorrow rather than anger.
His pack stands in a ring below, growling with bared fangs.
The hero stands before the rock, the horn at the side beginning to glow.

[Composition]
The wolf king on the rock towers over the upper two thirds; the hero is small at the bottom center, seen from behind.
```

### 05r_ending　場面5：正解（エンディング）

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Morning in the village at the edge of the forest.
The King of Wolves, huge and calm, stands at the village gate beside the hero, who holds the shining horn.
The old elder bows deeply, weeping with joy; villagers come out with baskets, children run toward the wolves.

[Composition]
The meeting of the wolf king and the elder is the visual center; the hero is at the lower left, seen in three-quarter rear view.
```

### 05b_bad　場面5：バッドエンド

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
A grassy hollow in the moonlit glade.
The hero lies sprawled in the grass, seen from behind, buried under a heap of playful wolf cubs: one chews an ear of the hood, one sits on the back, others tug at the cloak.
On the great rock above, the King of Wolves watches and yawns widely.

[Composition]
The heap of cubs on the hero is the visual center at the bottom; the yawning wolf king is at the upper right.
```
