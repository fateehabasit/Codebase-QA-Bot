\# Test Results — Codebase Q\&A Bot



Tested against: OOP-Social-Network-Application (C++/SFML)

LLM: Groq (llama-3.1-8b-instant) | Vector store: ChromaDB | Embeddings: all-MiniLM-L6-v2


Initial Test:

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


## Retrieval Improvements Applied Test

Switched from flat 800-char chunking to Parent Document Retriever (small child
chunks used for matching, whole-file parent chunks returned as context) + 
cross-encoder reranking (retrieve broad, rerank to top 4) + stricter prompt 
instructions against behavioral inference. Re-ran all 5 original questions below.

## Q1: How are memories handled?
**Answer**: Described the Memory class (inherits from Post), its constructor fields, the ShareMemoryByID method that creates and adds memories, Display/DisplayWithComments methods, memory ID generation (prefix "m" + post count), and storage/cleanup via the post manager and user's post list.
**Correct?** Yes — more complete than the original answer (added ShareMemoryByID and ID generation details not mentioned before).
**Sources**: Memory.cpp, Memory.h, SocialNetworkApp.cpp, SocialNetworkGUI.cpp

## Q2: How does the SFML GUI get set up and rendered?
**Answer**: Now correctly includes HandleEvents() and Run() — previously missing entirely. Describes window/font initialization, InputBox/Button/Text object creation, the Draw() rendering flow, and the full GUI loop (Run() calls HandleEvents() then Draw() repeatedly until the window closes).
**Correct?** Yes — retrieval gap from before is fully resolved.
**Sources**: InputBox.h, Button.h, SocialNetworkGUI.h

## Q3: How is a new user added to the network?
**Answer**: Correctly explained that LoadUsers() only loads existing users from Users.txt, and explicitly noted no manual add-user function exists in the codebase. Suggested a possible AddUser() implementation but clearly labeled it as a proposed addition, not existing code.
**Correct?** Yes — bot again correctly avoided hallucinating a nonexistent function as real.
**Sources**: SocialNetworkApp.cpp, User.cpp

## Q4: How are user friends handled?
**Answer**: Described the User** friends array, AddFriend's resize-by-one-and-copy logic, getFriends, getFriendCount, ViewFriendList, and AddFriend's self/null checks.
**Correct?** Yes
**Sources**: User.cpp, User.h, SocialNetworkApp.cpp

## Q5: What data structure stores likes and comments?
**Answer**: Correctly identified likedBy and comments as fixed-size arrays (size 10), and accurately described that AddLike/AddComment return without adding once the array is full. No more incorrect "no fixed capacity" claim.
**Correct?** Yes — previous factual error fully corrected.
**Sources**: Post.cpp, Post.h, SocialNetworkApp.h

## Summary
- 5/5 correct after retrieval improvements (up from 3/5 correct)
- Root causes identified and fixed:
  - Q2 gap was a retrieval-completeness issue (chunking split HandleEvents from surrounding context) — fixed by Parent Document Retriever returning whole files as context
  - Q5 error was a behavioral hallucination from incomplete context — fixed by fuller context + explicit prompt instruction against inferring unstated behavior
- Q3 continues to demonstrate correct hallucination avoidance (bot distinguishes "codebase doesn't have this" from "here's a suggested addition")
- Overall: ChromaDB + Parent Document Retriever + cross-encoder reranking + Groq LLM, all 5 test questions passing