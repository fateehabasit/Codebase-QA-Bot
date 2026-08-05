\# Test Results — Codebase Q\&A Bot



Tested against: OOP-Social-Network-Application (C++/SFML)

LLM: Groq (llama-3.1-8b-instant) | Vector store: ChromaDB | Embeddings: all-MiniLM-L6-v2



\## Q1: How are memories handled?

\*\*Answer\*\*: Explained the `Memory` class (inherits from `Post`), its constructor fields (id, text, date, sharedBy, originalPost, memoryText), how memories are created/added via SocialNetworkApp, and how they're displayed in the timeline.

\*\*Correct?\*\* Yes

\*\*Sources\*\*: Memory.h, Memory.cpp, SocialNetworkApp.cpp



\## Q2: How does the SFML GUI get set up and rendered?

\*\*Answer\*\*: Correctly described window/font initialization and general Draw() flow, but omitted HandleEvents() entirely — the actual event-handling implementation was never retrieved/cited.

\*\*Correct?\*\* Partially correct — structurally right, but incomplete. Missing function indicates retrieval limitation (k=4 too small / chunking splitting related logic), not a reasoning failure.

\*\*Sources\*\*: Button.h, SocialNetworkGUI.h, InputBox.h (HandleEvents implementation not among retrieved chunks)



\## Q3: How is a new user added to the network?

\*\*Answer\*\*: Identified that users are stored in a `users` array, and correctly noted that no explicit user-creation/add function exists in the codebase — new users appear to only be loaded from Users.txt via `LoadUsers()`, not created programmatically at runtime.

\*\*Correct?\*\* Yes — verified against the actual source; there genuinely is no AddUser-style function. The bot correctly avoided hallucinating one.

\*\*Sources\*\*: SocialNetworkApp.cpp, SocialNetworkGUI.cpp, User.cpp



\## Q4: How are user friends handled?

\*\*Answer\*\*: Explained the `friends` member (User\*\* dynamic array), the AddFriend method's resize-and-copy logic, getFriends, and how friends are displayed via viewHome/ViewFriendList.

\*\*Correct?\*\* Yes

\*\*Sources\*\*: User.cpp, SocialNetworkApp.cpp



\## Q5: What data structure stores likes and comments?

\*\*Answer\*\*: Correctly identified likedBy and comments as dynamic arrays of pointers (Entity\*\* and Comment\*\*), allocated via `new`. Incorrectly claimed likedBy "does not have a fixed capacity" — in reality, both likedBy and comments are allocated once at size 10 (nullptr check → new array\[10]) and are never resized; once full, further additions are simply rejected. The arrays are dynamic in the sense of being heap-allocated via `new`, but not dynamic in the sense of growing/resizing — the answer's phrasing implied the latter, which is inaccurate. No insight was given into why Entity (not User) is the base class for likes.

\*\*Correct?\*\* Partially incorrect — mischaracterized a fixed-size (size-10, non-resizing) heap array as lacking a capacity limit. Also shallow on the design-rationale part of the question.

\*\*Sources\*\*: Post.h, SocialNetworkApp.h, Post.cpp



\## Summary

\- 3/5 fully correct, 1 partially correct (missing function due to retrieval gap), 1 partially incorrect (mischaracterized array behavior)

\- Confirms retrieval quality (chunk size, k value) is the main bottleneck for completeness — Q2 missed HandleEvents() entirely because it wasn't among the top-k retrieved chunks, not because the LLM reasoned incorrectly

\- Q5 surfaced a subtler failure mode: the bot got the data structure's shape right (heap-allocated array of pointers) but wrong on its behavior (implied resizable, actually fixed at size 10 with no resize) — a good example of a plausible-sounding but behaviorally incorrect claim

\- Q3 (no AddUser function exists) is a genuine strength case: the bot correctly avoided hallucinating a function that doesn't exist in the codebase, instead accurately reporting the gap

\- Overall: retrieval completeness (Q2) is the clearest, most actionable fix for Course 3 (tune k, chunk size, or chunk-per-function). The Q5 error is more of a precision/prompting issue — worth revisiting once retrieval is tuned, e.g. by instructing the model to describe array behavior (capped vs. resizable) explicitly rather than just naming the type.

