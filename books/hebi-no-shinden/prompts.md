# 『羽毛の蛇の神殿と結び目の縄』画像プロンプト集

## 組み立て方

1枚のプロンプトは、次のブロックを上から順につなげて作ります。

```
[Style] + [Hero] + [Item] + [Tone] + [Scene] + [Composition] + [Frame]
```

- [Style] [Hero] [Frame] は全ページ共通です。一字一句変えずに使います。
- [Item] と [Tone] は、場面ごとに指定された方を選びます。[Item] は物語の途中で姿が変わる主人公の持ち物です。
- [Scene] と [Composition] は場面ごとに書き換えます。
- 表紙だけはカラーなので、[Style] の代わりに [Cover Style] を使います。
- 保存先は `books/hebi-no-shinden/images/raw/<ファイル名>_v1.png` です。候補が複数あるときは `_v2`、`_v3` と番号を増やします。
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
An old cord made of many thin hanging strings, all its knots come undone, the loose strands coiled at the hero's waist.
```

after は、姿が変わった後と表紙で使います。

```text
[Item: after]
The same cord of many hanging strings, now tied with rows of careful knots in a neat pattern, worn at the hero's waist.
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
A dense jungle at dusk; a great stepped stone pyramid rises above the canopy, crowned with a carved feathered serpent.
Before its dark entrance stands an enormous Golden Guardian, a giant of gold with a feathered-serpent crown and eyes shining like suns.
The hero stands small in the foreground, holding out the knotted cord.

[Composition]
The pyramid and the Golden Guardian fill the upper and middle part; the hero stands at the bottom center, seen from behind.
Keep the top quarter calm and dark so a title can be placed over it later.
```

### 01c_choice　場面1：選択

[Style] + [Hero] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A small village high in the Andes-like mountains above the clouds; terraced fields climb the slopes, llamas graze, stone houses with thatched roofs.
The crops are withering; villagers hold empty water jars.
The village elder in a woven poncho pleads with the hero; far below, a jungle and the tip of a stone temple.

[Composition]
The elder is at the center; the hero stands at the lower left, seen from behind; the terraces and the distant jungle are at the top.
```

### 01r_result　場面1：正解

[Style] + [Hero] + [Item: before] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Inside a stone house with a woven blanket on the wall.
The elder holds out an old cord made of many thin hanging strings, all its knots undone, toward the hero.

[Composition]
The cord with its loose strands is the visual center; the hero is at the lower left, seen in three-quarter rear view.
```

### 01b_bad　場面1：バッドエンド

[Style] + [Hero] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
A narrow village lane between stone houses on a mountainside.
The hero, older now, walks ahead seen from behind, followed by an absurdly long single-file line of llamas winding back up the terraces as far as the eye can see.
Villagers wait at the side of the lane, unable to cross.

[Composition]
The endless line of llamas winds from the lower left up to the top right; the hero leads at the lower left, seen from behind.
```

### 02c_choice　場面2：選択

[Style] + [Hero] + [Item: before] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A misty cloud forest of moss-covered trees on a mountain path, colorful birds among the branches.
Beside the path stands a carved stone waymarker covered in patterns of knotted cords.
The hero holds the loose strands of the cord before the stone; a bird perched on the stone tilts its head.

[Composition]
The carved waymarker is the visual center; the hero stands at the lower left, seen from behind.
```

### 02r_result　場面2：正解

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
The same misty cloud forest by the carved stone waymarker.
The hero holds up the cord, now tied with neat rows of knots; light shimmers along the strings.

[Composition]
The knotted cord is the visual center at the top; the hero is at the lower left, seen in three-quarter rear view; the waymarker is at the right.
```

### 02b_bad　場面2：バッドエンド

[Style] + [Hero] + [Item: before] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
A busy market in the mountain village.
The hero, seen from behind, sits at a stall heaped with beautifully elaborate decorative knots shaped like flowers and stars; customers crowd around admiring them.
The hero's boots have elaborate knotted laces.

[Composition]
The stall of fancy knots is the visual center; the hero sits at the lower left, seen from behind; the crowd fills the right.
```

### 03c_choice　場面3：選択

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Deep in the jungle, a great stepped stone pyramid crowned with a feathered serpent carving.
A grand staircase climbs its front, flanked by rows of stone jaguar statues with glinting eyes.
At the side, the mouth of an old dry water channel half hidden by vines leads into the foundations.
The hero stands at the foot, between the two.

[Composition]
The pyramid fills the upper part; the staircase is at the center, the vine-covered channel at the lower right; the hero is at the bottom center, seen from behind.
```

### 03r_result　場面3：正解

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Inside a dry stone water channel beneath the temple; the walls carved with feathered serpents swimming over waves.
At the far end, a bright golden glow.
The hero walks forward, seen from behind.

[Composition]
The channel recedes toward the golden glow at the center; the hero is in the foreground, seen from behind.
```

### 03b_bad　場面3：バッドエンド

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
An impossibly long stone staircase climbing up the front of the jungle pyramid, flanked by stone jaguars, stretching up into the clouds.
The hero, tiny, climbs on and on, seen from behind; far below, small village children wave.

[Composition]
The endless staircase rises from the bottom to the top; the hero is small in the middle; the waving children are at the bottom.
```

### 04c_choice　場面4：選択

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A great hall entirely of gold inside the temple: heaps of golden goblets, masks and llama statues.
Among them stand golden statues of people frozen with startled faces and outstretched hands.
On the floor before the hero lies a small golden feather ornament; footprints in the dust lead in, none lead out.

[Composition]
The golden hall fills the scene; the small feather on the floor is near the center; the hero stands at the lower left, seen from behind.
```

### 04r_result　場面4：正解

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
The far end of the golden hall: a huge stone door, the water gate, with the sound of water behind it.
Before it stands an enormous Golden Guardian, a giant of gold with a crown of a feathered serpent and eyes shining like suns.
The hero walks toward it, seen from behind.

[Composition]
The Golden Guardian and the stone door fill the upper two thirds; the hero is small at the bottom center, seen from behind.
```

### 04b_bad　場面4：バッドエンド

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
The golden hall, years later; the hero has become a golden statue with a startled face, holding a feather ornament.
Travelers line up to rub the statue's nose, which shines brighter than everything else.

[Composition]
The golden statue of the hero is at the lower left, seen in three-quarter rear view; the queue of travelers fills the right.
```

### 05c_choice　場面5：選択

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Before the stone water gate, the enormous Golden Guardian looms over the hero, one hand raised, eyes shining.
Golden statues of startled people lie at its feet.
The hero stands before it, the knotted cord at the waist.

[Composition]
The Golden Guardian towers over the upper two thirds; the hero is small at the bottom center, seen from behind.
```

### 05r_ending　場面5：正解（エンディング）

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
The high mountain village in sunshine: water rushes down stone channels into the terraced fields, which are green again.
Villagers in woven ponchos dance with flowers at a festival; llamas wear flower garlands; far below, the jungle temple.
The hero stands at the edge of the terraces, the knotted cord at the waist.

[Composition]
The festival and the green terraces fill the scene; the hero is at the lower left, seen in three-quarter rear view.
```

### 05b_bad　場面5：バッドエンド

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
Before the stone water gate, the Golden Guardian sits listening with its chin in its hand, looking amused.
The hero, seen from behind, shouts with arms raised; beside the hero rises a tall stack of thick ledgers.

[Composition]
The amused Guardian is at the upper right; the stack of ledgers in the middle; the shouting hero is at the lower left, seen from behind.
```
