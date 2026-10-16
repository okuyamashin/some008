# 『竜の迷宮と錆びた剣』画像プロンプト集

## 組み立て方

1枚のプロンプトは、次のブロックを上から順につなげて作ります。

```
[Style] + [Hero] + [Item] + [Tone] + [Scene] + [Composition] + [Frame]
```

- [Style] [Hero] [Frame] は全ページ共通です。一字一句変えずに使います。
- [Item] と [Tone] は、場面ごとに指定された方を選びます。[Item] は物語の途中で姿が変わる主人公の持ち物で、この本では剣です。
- [Scene] と [Composition] は場面ごとに書き換えます。
- 表紙だけはカラーなので、[Style] の代わりに [Cover Style] を使います。
- 保存先は `books/ryu-no-meikyu/images/raw/<ファイル名>_v1.png` です。候補が複数あるときは `_v2`、`_v3` と番号を増やします。

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
Long dark hooded cloak, simple leather armor.
```

### [Item]（どちらか1つ）

before（錆びた剣）は、場面2で剣を抜く前と、剣を抜かなかったバッドエンドで使います。

```text
[Item: before]
A dull, chipped, rusty short sword sheathed in a worn scabbard at the hip.
```

after（聖剣）は、場面2で剣を抜いた後と表紙で使います。

```text
[Item: after]
An ornate longsword with a cross-shaped hilt and a round pommel, carried in a scabbard on the back.
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
| 01c_village_request | 村：依頼を受けるか | before | story | 未作成 |
| 01r_village_map | 地図をもらう | before | story | 未作成 |
| 01b_village_turnip | カブを差し出す | なし | bad ending | 未作成 |
| 02c_forest_sword | 森：剣が刺さっている | before | story | v1・v2 作成済み |
| 02r_forest_excalibur | 剣を抜く | after（手に持つ） | story | 未作成 |
| 02b_forest_porter | 子どもの荷物持ち | before | bad ending | 未作成 |
| 03c_dungeon_entrance | 入口：大扉か小さな穴か | after | story | 未作成 |
| 03r_dungeon_passage | 隠し通路 | after | story | 未作成 |
| 03b_dungeon_knock | 竜にセールスと間違えられる | after | bad ending | 未作成 |
| 04c_cellar_chest | 地下の宝箱 | after | story | 未作成 |
| 04r_cellar_onward | 竜の巣へ | after | story | 未作成 |
| 04b_cellar_mimic | 泣くミミック | after | bad ending | v1 作成済み |
| 05c_lair_dragon | ドラゴンとの対決 | after | story | 未作成 |
| 05r_lair_treasure | 財宝を持ち帰る（エンディング） | after | story | 未作成 |
| 05b_lair_tavern | 酒場で誰にも信じてもらえない | after | bad ending | 未作成 |

### 00_cover　表紙

[Cover Style] + [Hero] + [Item: after] + 以下 + [Cover Frame]

```text
[Scene]
A vast underground cavern lit by the glow of an enormous hoard of gold coins, goblets and jewels.
A huge black dragon is coiled on top of the hoard, wings half spread, smoke curling from its nostrils, glaring down.
The hero stands small in the foreground, has drawn the ornate longsword and holds it ready, facing the dragon.

[Composition]
The dragon fills the upper and middle part of the image; the hero stands at the bottom center, seen from behind.
Keep the top quarter calm and dark so a title can be placed over it later.
```

### 01c_village_request　村：依頼を受けるか

[Style] + [Hero] + [Item: before] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A small medieval village square at dusk, with thatched cottages and a stone well.
An elderly village chief with a long white beard and a wooden staff stands before the hero, pleading with open hands.
Worried villagers, including mothers holding children, gather behind him.
Far away on a distant mountain, a thin column of smoke rises from a dark cave mouth.

[Composition]
The chief and villagers are at the center; the hero stands at the lower left, seen from behind.
The distant mountain with the smoke is small, at the upper right.
```

### 01r_village_map　地図をもらう

[Style] + [Hero] + [Item: before] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
Inside a humble village cottage, lit by a hearth fire.
The elderly chief solemnly hands a rolled parchment map to the hero.
The map is partly unrolled, showing drawn mountains, a forest and a cave marked with a small dragon symbol, with no writing on it.
Village children peek in through the small window, full of hope.

[Composition]
The map passing between the two hands is the visual center; the hero is at the lower left, seen in three-quarter rear view.
```

### 01b_village_turnip　カブを差し出す（バッドエンド）

[Style] + [Hero] + [Tone: bad ending] + 以下 + [Frame]（Item は付けない）

```text
[Scene]
Thirty years later, on a farm field at the edge of the village.
The hero, now an old stooped farmer in a hooded peasant smock with a hoe at his side, seen from behind, solemnly presents an enormous turnip with both hands.
Before him stands a young knight in shining armor, proudly showing off a cart overflowing with gold coins and dragon treasure.
The moment is drawn with the dignity of a royal ceremony.

[Composition]
The giant turnip is the visual center, held up between the old farmer and the knight; the farmer is at the lower left, seen from behind.
```

### 02c_forest_sword　森：剣が刺さっている（作成済み）

[Style] + [Hero] + [Item: before] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A narrow path through an ancient, dense forest.
In a small clearing, an ornate longsword is thrust deep into a moss-covered stone.
A single shaft of light falls through a gap in the canopy onto the sword, drawn as fine parallel engraved lines.
The hero has stopped on the path and is looking at the sword, hesitating.
Gnarled roots, ferns, thin mist between the trees. Quiet, solemn, mysterious mood.

[Composition]
The sword is the visual center; the hero stands at the lower left, about one third of the image height.
```

### 02r_forest_excalibur　剣を抜く

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
The same forest clearing with the moss-covered stone.
The hero has just pulled the ornate longsword from the stone and holds it high overhead with both hands.
The blade blazes with light, drawn as radiating engraved lines; birds burst up from the trees.
The old rusty short sword lies discarded on the stone.

[Composition]
The raised sword is at the top center; the hero stands on the stone, seen in three-quarter rear view.
```

### 02b_forest_porter　子どもの荷物持ち（バッドエンド）

[Style] + [Hero] + [Item: before] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
A forest road.
A small village child of about eight, in a simple tunic and a little crown of leaves, proudly holds the ornate longsword aloft, lit by a shaft of light.
Behind the child, the hero trudges along, bent under an absurdly tall stack of luggage: bedrolls, pots, pans, sacks and a birdcage.
Drawn like a solemn painting of a king's procession.

[Composition]
The child is at the upper center, striding forward; the hero follows at the lower left, seen from behind.
```

### 03c_dungeon_entrance　入口：大扉か小さな穴か

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A rocky mountainside at the mouth of the dungeon.
A gigantic carved stone double door with heavy iron rings and dragon-head carvings; scorch marks and scattered old bones lie in front of it.
Beside it, half-hidden by ivy and rocks, is a small dark hole just large enough to crawl through.
The hero stands between the two, looking from one to the other.

[Composition]
The great door fills the right half; the small hole is at the lower left; the hero stands at the bottom center, seen from behind.
```

### 03r_dungeon_passage　隠し通路

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A narrow secret passage inside the mountain, with ancient carved steps leading down.
The hero walks down carefully, holding a torch; its light falls on old carvings on the walls.
A few mice scurry ahead. Far below, a faint warm glow.

[Composition]
The passage recedes from the foreground to the glow at the center; the hero is in the foreground, seen from behind.
```

### 03b_dungeon_knock　竜にセールスと間違えられる（バッドエンド）

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
The gigantic carved stone door of the dungeon, now opened just a crack.
A huge dragon's head pokes out through the gap with half-lidded, irritated eyes, a wisp of smoke from one nostril, one claw holding the door like a householder.
A blank wooden plaque hangs on the door.
The hero stands on the doorstep, one hand still raised in mid-knock.

[Composition]
The dragon's head in the door gap is the visual center; the hero is at the lower left, seen from behind.
```

（張り紙の文字「竜在宅中・御用の方はノックを」は、絵には入れずHTML側で重ねます。）

### 04c_cellar_chest　地下の宝箱

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A dark stone cellar deep in the dungeon, lit by a single candle on the floor.
A large, ornate iron-bound treasure chest sits in the middle with its lid closed; a few gold coins lie scattered in front of it.
Look closely: the lid is lifted a hair's breadth, and the tip of a pointed tooth glints in the gap.
The hero stands and studies the chest. Beyond it, a dark archway leads on, with a faint warm glow.

[Composition]
The chest is the visual center; the hero stands at the lower left, seen from behind; the archway is at the upper right.
```

### 04r_cellar_onward　竜の巣へ

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
A long corridor descending deeper into the dungeon.
The hero strides forward without looking back, toward a vast cavern at the far end glowing with firelight.
Far behind him, back in the cellar, the treasure chest's lid is raised slightly and a single disappointed eye peers after him.

[Composition]
The glowing cavern is at the upper center; the hero walks away in the middle, seen from behind; the small chest is at the lower right.
```

### 04b_cellar_mimic　泣くミミック（バッドエンド・作成済み）

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
A dark stone cellar deep in a dungeon, lit by a single candle on the floor.
A large, ornate iron-bound treasure chest sits with its lid half open.
It is a mimic: rows of jagged teeth line the rim of the lid, and a long tongue hangs out.
Two large, sorrowful eyes peer out from the dark gap under the lid, and heavy tears stream down the front of the chest and pool on the floor.
The hero sits on the floor beside the chest, shoulders slumped, one hand resting gently on the lid, listening patiently.
Thick cobwebs stretch between the hero's cloak and the chest, and many burned-down candle stubs surround them, suggesting they have been sitting like this for a very long time.

[Composition]
The weeping mimic is the visual center; the hero sits at the lower left, seen from behind.
```

### 05c_lair_dragon　ドラゴンとの対決

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
The dragon's lair: a vast cavern with a mountain of gold coins and treasure.
A huge black dragon rears up on the hoard, wings spread wide, fire glowing in its open throat.
The hero stands at the foot of the hoard, drawing the ornate longsword from the scabbard on the back.

[Composition]
The dragon towers over the upper two thirds; the hero is small at the bottom center, seen from behind.
```

### 05r_lair_treasure　財宝を持ち帰る（エンディング）

[Style] + [Hero] + [Item: after] + [Tone: story] + 以下 + [Frame]

```text
[Scene]
The village square in bright morning sunlight, decorated with blank banners and garlands.
Villagers cheer and throw flowers; children run alongside a cart piled with gold and a great dragon's horn.
The elderly chief raises both arms in welcome.
The hero walks beside the cart, the ornate longsword on the back.

[Composition]
The cart of treasure and the cheering crowd fill the center; the hero is at the lower left, seen in three-quarter rear view.
```

### 05b_lair_tavern　酒場で誰にも信じてもらえない（バッドエンド）

[Style] + [Hero] + [Item: after] + [Tone: bad ending] + 以下 + [Frame]

```text
[Scene]
A dim village tavern at night, lit by a few candles.
The hero stands on a bench with a tankard raised, the other arm flung wide, telling the tale of the dragon with grand gestures.
Nobody is listening: one patron sleeps face down on a table, others play cards, and the barkeeper polishes a mug with a bored look.
A dog yawns under the table.

[Composition]
The hero on the bench is at the left, seen in three-quarter rear view; the indifferent patrons fill the right half.
```
