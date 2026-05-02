# Evaluation Report

- Scene is unstable because the robot hand is still actively holding the card between `s4/00_capture.jpg` and `s5/00_capture.jpg`.
- It is our turn.
- Workflow state is merged as `acting` because the cached sequence says `atom_idle`, but visual evidence shows the `view_card` action is still in progress.
- Blind assignment is taken from durable cache: robot `big_blind`, opponent `small_blind` and dealer.
- No community cards are visible.
- Inventory and bet counts are carried forward from the last settled parsed state because the current frame does not provide a better count and no bet movement is evident.
