# showdown_outcome_agent

Completed status:

> Showdown appears to be visible: there are face-up hole cards on the table and a full five-card board is dealt.
>
> What I can read:
> - Robot hand at bottom center looks face-up: `Q♥` and `10♠`.
> - Community cards in the middle look like `J♥`, `A♣`, `K♠`, `4♣`, and `K♦` or another king-valued card.
> - An opponent hand near the top/middle also appears face-up, but the exact ranks/suits are less clear from this angle.
>
> Best-hand evidence:
> - If the board is read correctly, the robot has `A-K-Q-J-10`, which is a Broadway straight.
> - That would be strong win evidence against a lower opponent hand.
>
> Confidence notes:
> - The robot hole cards are readable directly from the image.
> - One or more community cards are partially obscured/angled, so the exact board is not 100% certain.
> - Because of that, I can say this looks like showdown with strong win evidence, but I would not treat it as fully certain without a cleaner read.
>
> Recommended label:
> - `showdown_visible`
> - `likely_win` if the board read is correct

