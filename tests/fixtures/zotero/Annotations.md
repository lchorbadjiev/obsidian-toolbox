# Annotations  
(3/26/2026, 5:55:13 PM)

“So, what’s the problem? Simply this: Refactoring is risky. It requires changes to working code that can introduce subtle bugs. Refactoring, if not done properly,can set you back days, even weeks. And refactoring becomes riskier when prac-ticed informally or ad hoc.” (“Refactoring”, p. xi)

“When my coauthors and I wrote Design Patterns, wementioned that design patterns provide targets for refactorings. However, identi-fying the target is only one part of the problem; transforming your code so thatyou get there is another challenge” (“Refactoring”, p. xi)

“But don’t be fooled. Understanding the mechanics of such refactorings is thekey to refactoring in a disciplined way. The refactorings in this book will helpyou change your code one small step at a time, thus reducing the risks of evolving” (“Refactoring”, p. xi)

“your design” (“Refactoring”, p. xii)

“My first experience with disciplined, “one step at a time” refactoring was when I was pair-programming at 30,000 feet with Kent Beck. He made sure that weapplied refactorings from this book’s catalog one step at a time. I was amazed at how well this practice worked. Not only did my confidence in the resulting codeincrease, I also felt less stressed. I highly recommend you try these refactorings:You and your code will feel much better for it.” (“Refactoring”, p. xii)

“How do you feel about this story? Do you think the consultant was right tosuggest further cleanup? Or do you follow that old engineering adage, “if it works,don’t fix it”?I must admit to some bias here. I was that consultant. Six months later, the project failed, in large part because the code was too complex to debug or tuneto acceptable performance.” (“Refactoring”, p. xiv)

“What Is Refactoring?Refactoring is the process of changing a software system in a way that does notalter the external behavior of the code yet improves its internal structure. It is a disciplined way to clean up code that minimizes the chances of introducing bugs. In essence, when you refactor, you are improving the design of the code after it has been written.” (“Refactoring”, p. xiv)

“With refactoring, the balance of work changes. I found that design, rather thanoccurring all up front, occurs continuously during development. As I build thesystem, I learn how to improve the design. The result of this interaction is aprogram whose design stays good as development continues.” (“Refactoring”, p. xv)

“This book is a guide to refactoring; it is written for a professional programmer.My aim is to show you how to do refactoring in a controlled and efficient manner.You will learn to refactor in such a way that you don’t introduce bugs into the code but methodically improve its structure.” (“Refactoring”, p. xv)

“If you want to actually do refactoring, read the first four chapters completely,then skip-read the catalog. Read enough of the catalog to know, roughly,what is in there. You don’t have to understand all the details. When youactually need to carry out a refactoring, read the refactoring in detail and use it to help you. The catalog is a reference section, so you probably won’twant to read it in one go.” (“Refactoring”, p. xviii)

“Two of the leading early proponents of refactoring were Ward Cunninghamand Kent Beck. They used it as a foundation of development in the early days and adapted their development processes to take advantage of it.” (“Refactoring”, p. xviii)

“Even with all that research to draw on, I still needed a lot of help to write thisbook. The first edition drew greatly on experience and encouragement from Kent Beck. He first introduced me to refactoring, inspired me to start writing notes to record refactorings, and helped form them into finished prose. He cameup with the idea of Code Smells. I often feel he would have written the firstedition better than I had done—if we wasn’t writing the foundation book forExtreme Programming instead.” (“Refactoring”, p. xix)

“I’m thus in the classic bind of anyone who wants to describe techniques that are useful for real-world programs. Frankly, it is not worth the effort to do all the refactoring that I’m going to show you on the small program I will be using.But if the code I’m showing you is part of a larger system, then the refactoringbecomes important. Just look at my example and imagine it in the context of a much larger system.” (“Refactoring”, p. 1)

“What are your thoughts on the design of this program? The first thing I’d say isthat it’s tolerable as it is—a program so short doesn’t require any deep structureto be comprehensible” (“Refactoring”, p. 3)

“Given that the program works, isn’t any statement about its structure merely an aesthetic judgment, a dislike of “ugly” code? After all, the compiler doesn’t care whether the code is ugly or clean. But when I change the system, there isa human involved, and humans do care. A poorly designed system is hard to change—because it is difficult to figure out what to change and how these changeswill interact with the existing code to get the behavior I want.” (“Refactoring”, p. 4)

“Thus, if I’m faced with modifying a program with hundreds of lines of code,I’d rather it be structured into a set of functions and other program elements thatallow me to understand more easily what the program is doing. If the program lacks structure, it’s usually easier for me to add structure to the program first,and then make the change I need” (“Refactoring”, p. 4)

“When you have to add a feature to a program but the codeis not structured in a conve-nient way, first refactor theprogram to make it easy to addthe feature, then add thefeature.” (“Refactoring”, p. 4)

“If I’m writinga program that will never change again, this kind of copy-and-paste is fine. But if it’s a long-lived program, then duplication is a menace.” (“Refactoring”, p. 4)

“If” (“Refactoring”, p. 4)

“Let me stress that it’s these changes that drive the need to perform refactoring.If the code works and doesn’t ever need to change, it’s perfectly fine to leave it alone. It would be nice to improve it, but unless someone needs to understand it, it isn’t causing any real harm. Yet as soon as someone does need to under-stand how that code works, and struggles to follow it, then you have to dosomething about it” (“Refactoring”, p. 5)

“Whenever I do refactoring, the first step is always the same. I need to ensure Ihave a solid set of tests for that section of code. The tests are essential becauseeven though I will follow refactorings structured to avoid most of the opportunitiesfor introducing bugs, I’m still human and still make mistakes.” (“Refactoring”, p. 5)

“It is vital to make tests self-checking.” (“Refactoring”, p. 5)

“Before you start refactoring,make sure you have a solidsuite of tests. These tests mustbe self-checking.” (“Refactoring”, p. 5)

“As I do the refactoring, I’ll lean on thetests. I think of them as a bug detectorto protect me against my own mistakes” (“Refactoring”, p. 5)

“As I look at this chunk, I conclude that it’s calculating the charge for one per-formance. That conclusion is a piece of insight about the code. But as WardCunningham puts it, this understanding is in my head—a notoriously volatile form of storage. I need to persist it by moving it from my head back into thecode itself. That way, should I come back to it later, the code will tell me whatit’s doing—I don’t have to figure it out again.” (“Refactoring”, p. 7)

“When I want to turn a chunk of code into a function like this, I have a procedurefor doing it that minimizes my chances of getting it wrong. I wrote down thisprocedure and, to make it easy to reference, named it Extract Function (106).” (“Refactoring”, p. 7)

“Once I’ve made this change, I immediately compile and test to see if I’ve broken anything. It’s an important habit to test after every refactoring, however simple. Mistakes are easy to make—at least, I find them easy to make. Testing after each change means that when I make a mistake, I only have a small change to considerin order to spot the error, which makes it far easier to find and fix. This is theessence of the refactoring process: small changes and testing after each change.” (“Refactoring”, p. 8)

“Refactoring changes the programs in small steps, so if youmake a mistake, it is easy tofind where the bug is” (“Refactoring”, p. 8)

“I commit after each successfulrefactoring, so I can easily get back to a working state should I mess up later. Ithen squash changes into more significant commits before I push the changes toa shared repository.” (“Refactoring”, p. 9)

“Once I’ve used Extract Function (106), I take a look at what I’ve extracted to seeif there are any quick and easy things I can do to clarify the extracted function.” (“Refactoring”, p. 9)

“It’s my coding standard to always call the return value from a function “result”” (“Refactoring”, p. 9)

“Any fool can write code that a computer can understand.Good programmers write codethat humans can understand.” (“Refactoring”, p. 10)

“Is this renaming worth the effort? Ab-solutely. Good code should clearly com-municate what it is doing, and variablenames are a key to clear code. Never beafraid to change names to improveclarity” (“Refactoring”, p. 10)

“WhenI’m breaking down a long function, I like to get rid of variables like play, because temporary variables create a lot of locally scoped names that complicateextractions. The refactoring I will use here is Replace Temp with Query (178)” (“Refactoring”, p. 11)

“I compile-test-commit, and then use Inline Variable (123).” (“Refactoring”, p. 11)

“This refactoring alarms some programmers. Previously, the code to look upthe play was executed once in each loop iteration; now, it’s executed thrice. I’lltalk about the interplay of refactoring and performance later, but for the momentI’ll just observe that this change is unlikely to significantly affect performance, and even if it were, it is much easier to improve the performance of a well-factored code base.” (“Refactoring”, p. 14)

“The great benefit of removing local variables is that it makes it much easier todo extractions, since there is less local scope to deal with. Indeed, usually I’ll take out local variables before I do any extractions.” (“Refactoring”, p. 14)

“Naming is both important and tricky. Breaking a large function into smaller ones only adds value if the names are good. With good names, I don’t have toread the body of the function to see what it does. But it’s hard to get names rightthe first time, so I use the best name I can think of for the moment, and don’thesitate to rename it later. Often, it takes a second pass through some code torealize what the best name really is” (“Refactoring”, p. 18)

“Storing money as integer cents is a common approach—it avoidsthe dangers of storing fractional monetary values as floats but allows me to usearithmetic operators. Whenever I want to display such a penny-integer number, however, I need a decimal, so my formatting function should take care of thedivision.” (“Refactoring”, p. 18)

“Most programmers, even experienced ones,are poor judges of how code actually performs. Many of our intuitions are broken by clever compilers, modern caching techniques, and the like. The performance of software usually depends on just a few parts of the code, and changes anywhereelse don’t make an appreciable difference.” (“Refactoring”, p. 20)

“But “mostly” isn’t the same as “alwaysly.” Sometimes a refactoring will have asignificant performance implication. Even then, I usually go ahead and do it, be-cause it’s much easier to tune the performance of well-factored code. If I introducea significant performance issue during refactoring, I spend time on performance tuning afterwards. It may be that this leads to reversing some of the refactoringI did earlier—but most of the time, due to the refactoring, I can apply a more effective performance-tuning enhancement instead. I end up with code that’s bothclearer and faster.” (“Refactoring”, p. 20)

“So, my overall advice on performance with refactoring is: Most of the time you should ignore it. If your refactoring introduces performance slow-downs, finishrefactoring first and do performance tuning afterwards.” (“Refactoring”, p. 20)

“I confess I don’t always take quite as short steps as these—but whenever things get difficult, my first reaction is to take shorter steps. In particular, should a testfail during a refactoring, if I can’t immediately see and fix the problem, I’ll revertto my last good commit and redo what I just did with smaller steps. That worksbecause I commit so frequently and because small steps are the key to moving quickly, particularly when working with difficult code.” (“Refactoring”, p. 21)

“So far, my refactoring has focused on adding enough structure to the function so that I can understand it and see it in terms of its logical parts. This is often the case early in refactoring. Breaking down complicated chunks into small pieces is important, as is naming things well. Now, I can begin to focus more on the functionality change I want to make” (“Refactoring”, p. 24)

“There are various ways to do this, but one of my favorite techniques is Split Phase (154). My aim here is to divide the logic into two parts: one that calculates the data required for the statement, the other that renders it into text or HTML. The first phase creates an intermediate data structure that it passes to the second.” (“Refactoring”, p. 24)

“The idiom result = Object.assign({}, aPerformance) looks very odd to people unfamiliar to JavaScript. It performs a shallow copy.” (“Refactoring”, p. 27)

“If all else is equal, more code is bad—but rarely is all else equal.” (“Refactoring”, p. 33)

“Brevity is the soul of wit, but clarity is the soul of evolvable software.” (“Refactoring”, p. 33)

“When programming, follow the camping rule: Always leave the code base healthier than when you found it.” (“Refactoring”, p. 34)

“I always have to strike a balance between all the refactorings I could do and adding new features. At the moment, most people underprioritize refactoring—but there still is a balance. My rule is a variation on the camping rule: Always leave the code base healthier than when you found it. It will never be perfect, but it should be better.” (“Refactoring”, p. 34)

“The core refactoring is Replace Conditional with Polymorphism (272), which changes a hunk of conditional code with polymorphism.” (“Refactoring”, p. 34)

“I’m not saying compile-test-commit all the time any more, as I suspect you’re getting tired of reading it. But I still do it at every opportunity. I do sometimes get tired of doing it—and give mistakes the chance to bite me. Then I learn and get back into the rhythm.” (“Refactoring”, p. 37)

“As is often the case with refactoring, the early stages were mostly driven by trying to understand what was going on. A common sequence is: Read the code, gain some insight, and use refactoring to move that insight from your head back into the code. The clearer code then makes it easier to understand it, leading to deeper insights and a beneficial positive feedback loop.” (“Refactoring”, p. 43)

“The true test of good code is how easy it is to change it.” (“Refactoring”, p. 43)

“I’m talking about improving the code—but programmers love to argue about what good code looks like. I know some people object to my preference for small, well-named functions. If we consider this to be a matter of aesthetics, where nothing is either good or bad but thinking makes it so, we lack any guide but personal taste. I believe, however, that we can go beyond taste and say that the true test of good code is how easy it is to change it. Code should be obvious: When someone needs to make a change, they should be able to find the code to be changed easily and to make the change quickly without introducing any errors.” (“Refactoring”, p. 43)

“But the most important thing to learn from this example is the rhythm of refactoring. Whenever I’ve shown people how I refactor, they are surprised by how small my steps are, each step leaving the code in a working state that compiles and passes its tests. I was just as surprised myself when Kent Beck showed me how to do this in a hotel room in Detroit two decades ago. The key to effective refactoring is recognizing that you go faster when you take tiny steps, the code is never broken, and you can compose those small steps into substantial changes. Remember that—and the rest is silence.” (“Refactoring”, p. 44)

“Like many terms in software development, “refactoring” is often used veryloosely by practitioners” (“Refactoring”, p. 45)

“Refactoring (noun): a change made to the internal structure of software tomake it easier to understand and cheaper to modify without changing itsobservable behavior.” (“Refactoring”, p. 45)

“Refactoring (verb): to restructure software by applying a series of refactoringswithout changing its observable behavior.” (“Refactoring”, p. 45)

“So I might spend a couple of hours refactoring, during which I would apply a few dozen individual refactorings.” (“Refactoring”, p. 45)

“Refactoring is all about applying small behavior-preserving steps and making a big change by stringing together a sequence ofthese behavior-preserving steps” (“Refactoring”, p. 45)

“Each individual refactoring is either pretty small” (“Refactoring”, p. 45)

“itself or a combination of small steps. As a result, when I’m refactoring, my codedoesn’t spend much time in a broken state, allowing me to stop at any moment even if I haven’t finished.” (“Refactoring”, p. 46)

“If someone says their code wasbroken for a couple of dayswhile they are refactoring, youcan be pretty sure they werenot refactoring” (“Refactoring”, p. 46)

“I use “restructuring” as a general termto mean any kind of reorganizing orcleaning up of a code base, and seerefactoring as a particular kind of restruc-turing. Refactoring may seem inefficientto people who first come across it andwatch me making lots of tiny steps, whena single bigger step would do. But thetiny steps allow me to go faster becausethey compose so well—and, crucially, because I don’t spend any time debugging.In my definitions, I use the phrase “observable behavior.” This is a deliberately loose term, indicating that the code should, overall, do just the same things itdid before I started. It doesn’t mean it will work exactly the same—for example, Extract Function (106) will alter the call stack, so performance characteristics mightchange—but nothing should change that the user should care about. In particular,interfaces to modules often change due to such refactorings as Change FunctionDeclaration (124) and Move Function (198). Any bugs that I notice during refactoringshould still be present after refactoring (though I can fix latent bugs that nobodyhas observed yet).” (“Refactoring”, p. 46)

“The Two HatsKent Beck came up with a metaphor of the two hats. When I use refactoring todevelop software, I divide my time between two distinct activities: adding functionality and refactoring. When I add functionality, I shouldn’t be changing existingcode; I’m just adding new capabilities. I measure my progress by adding testsand getting the tests to work. When I refactor, I make a point of not adding functionality; I only restructure the code. I don’t add any tests (unless I find acase I missed earlier); I only change tests when I have to accommodate a changein an interface.” (“Refactoring”, p. 46)

“I don’t want to claim refactoring is the cure for all software ills. It is no “silver bullet” (“Refactoring”, p. 47)

“Refactoring Improves the Design of SoftwareWithout refactoring, the internal design—the architecture—of software tends todecay. As people change code to achieve short-term goals, often without a full comprehension of the architecture, the code loses its structure. It becomes harderfor me to see the design by reading the code. Loss of the structure of code hasa cumulative effect. The harder it is to see the design in the code, the harder it is for me to preserve it, and the more rapidly it decays. Regular refactoring helpskeep the code in shape.” (“Refactoring”, p. 47)

“But there are likely to beother users of my source code. In a few months, a human will try to read my” (“Refactoring”, p. 47)

“code to make some changes. That user, who we often forget, is actually the mostimportant. Who cares if the computer takes a few more cycles to compile some-thing? Yet it does matter if it takes a programmer a week to make a change that would have taken only an hour with proper understanding of my code. The trouble is that when I’m trying to get the program to work, I’m not thinking about that future developer.” (“Refactoring”, p. 48)

“It takes a change of rhythm to make the code easierto understand. Refactoring helps me make my code more readable. Before refactoring, I have code that works but is not ideally structured. A little time spent on refactoring can make the code better communicate its purpose—say more clearly what I want” (“Refactoring”, p. 48)

“I’m not necessarily being altruistic about this. Often, this future developer ismyself. This makes refactoring even more important.” (“Refactoring”, p. 48)

“Refactoring Helps Me Find BugsHelp in understanding the code also means help in spotting bugs. I admit I’m not terribly good at finding bugs. Some people can read a lump of code and see bugs; I cannot. However, I find that if I refactor code, I work deeply on under-standing what the code does, and I put that new understanding right back intothe code. By clarifying the structure of the program, I clarify certain assumptionsI’ve made—to a point where even I can’t avoid spotting the bugs.It reminds me of a statement Kent Beck often makes about himself: “I’m not agreat programmer; I’m just a good programmer with great habits.” Refactoring helps me be much more effective at writing robust code.” (“Refactoring”, p. 48)

“I refer to this effect as the Design Stamina Hypothesis [mf-dsh]: By putting oureffort into a good internal design, we increase the stamina of the software effort,allowing us to go faster for longer. I can’t prove that this is the case, which is why I refer to it as a hypothesis. But it explains my experience, together with theexperience of hundreds of great programmers that I’ve got to know over my career.” (“Refactoring”, p. 50)

“Twenty years ago, the conventional wisdom was that to get this kind of gooddesign, it had to be completed before starting to program—because once we wrote the code, we could only face decay. Refactoring changes this picture.” (“Refactoring”, p. 50)

“Preparatory Refactoring—Making It Easier to Add a FeatureThe best time to refactor is just before I need to add a new feature to the codebase. As I do this, I look at the existing code and, often, see that if it were structured a little differently, my work would be much easier.” (“Refactoring”, p. 50)

““It’s like I want to go 100 miles east but instead of just traipsing through the woods, I’m going to drive 20 miles north to the highway and then I’m going to go 100 miles east at three times the speed I could have if I just went straightthere. When people are pushing you to just go straight there, sometimes you needto say, ‘Wait, I need to check the map and find the quickest route.’ The prepara-tory refactoring does that for me.”— Jessica Kerr,https://martinfowler.com/articles/preparatory-refactoring-example.html” (“Refactoring”, p. 51)

“Comprehension Refactoring: Making Code Easier to UnderstandBefore I can change some code, I need to understand what it does. This codemay have been written by me or by someone else. Whenever I have to think tounderstand what the code is doing, I ask myself if I can refactor the code to makethat understanding more immediately apparent.” (“Refactoring”, p. 51)

“Litter-Pickup RefactoringA variation of comprehension refactoring is when I understand what the code isdoing, but realize that it’s doing it badly. The logic is unnecessarily convoluted, or I see functions that are nearly identical and can be replaced by a single param-eterized function. There’s a bit of a tradeoff here. I don’t want to spend a lot oftime distracted from the task I’m currently doing, but I also don’t want to leavethe trash lying around and getting in the way of future changes. If it’s easy tochange, I’ll do it right away. If it’s a bit more effort to fix, I might make a noteof it and fix it when I’m done with my immediate task” (“Refactoring”, p. 52)

“Planned and Opportunistic RefactoringThe examples above—preparatory, comprehension, litter-pickup refactoring—areall opportunistic. I don’t set aside time at the beginning to spend on refactoring—instead, I do refactoring as part of adding a feature or fixing a bug. It’s partof my natural flow of programming. Whether I’m adding a feature or fixing abug, refactoring helps me do the immediate task and also sets me up to make future work easier. This is an important point that’s frequently missed. Refactoringisn’t an activity that’s separated from programming—any more than you set asidetime to write if statements. I don’t put time on my plans to do refactoring; mostrefactoring happens while I’m doing other things” (“Refactoring”, p. 52)

“You have to refactor when you run into ugly code—but excel-lent code needs plenty of refac-toring too.” (“Refactoring”, p. 52)

“It’s also a common error to see refac-toring as something people do to fix pastmistakes or clean up ugly code. Certainlyyou have to refactor when you run intougly code, but excellent code needsplenty of refactoring too. Whenever Iwrite code, I’m making tradeoffs—howmuch do I need to parameterize, whereto draw the lines between functions? The tradeoffs I made correctly for yesterday’sfeature set may no longer be the right ones for the new features I’m adding today.The advantage is that clean code is easier to refactor when I need to changethose tradeoffs to reflect the new reality.” (“Refactoring”, p. 52)

““for each desired change, make the change easy (warning: this may be hard),then make the easy change”— Kent Beck,https://twitter.com/kentbeck/status/250733358307500032” (“Refactoring”, p. 53)

“For a long time, people thought of writing software as a process of accretion:To add new features, we should be mostly adding new code. But good developersknow that, often, the fastest way to add a new feature is to change the code tomake it easy to add. Software should thus be never thought of as “done.”” (“Refactoring”, p. 53)

“All this doesn’t mean that planned refactoring is always wrong.” (“Refactoring”, p. 53)

“One bit of advice I’ve heard is to separate refactoring work and new featureadditions into different version-control commits. The big advantage of this is that they can be reviewed and approved independently. I’m not convinced of this,however. Too often, the refactorings are closely interwoven with adding newfeatures, and it’s not worth the time to separate them out. This can also removethe context for the refactoring, making the refactoring commits hard to justify.Each team should experiment to find what works for them; just remember thatseparating refactoring commits is not a self-evident principle—it’s only worthwhileif it makes life easier.” (“Refactoring”, p. 53)

“Long-Term Refactoring Most refactoring can be completed within a few minutes—hours at most. But there are some larger refactoring efforts that can take a team weeks to complete.” (“Refactoring”, p. 53)

“Even in such cases, I’m reluctant to have a team do dedicated refactoring. Often, a useful strategy is to agree to gradually work on the problem over the course of the next few weeks. Whenever anyone goes near any code that’s in the refactoring zone, they move it a little way in the direction they want to improve. This takes advantage of the fact that refactoring doesn’t break the code—each small change leaves everything in a still-working state.” (“Refactoring”, p. 53)

“Refactoring in a Code Review” (“Refactoring”, p. 54)

“How I’d embed refactoring into a code review depends on the nature of the review. The common pull request model, where a reviewer looks at code without the original author, doesn’t work too well. It’s better to have the original author of the code present because the author can provide context on the code and fully appreciate the reviewers’ intentions for their changes. I’ve had my best experiences with this by sitting one-on-one with the original author, going through the code and refactoring as we go.” (“Refactoring”, p. 54)

“The logical conclusion of this style is pair programming: continuous code review embedded within the process of programming.” (“Refactoring”, p. 54)

“Software developers are professionals. Our job is to build effective software as rapidly as we can. My experience is that refactoring is a big aid to building software quickly. If I need to add a new function and the design does not suit the change, I find it’s quicker to refactor first and then add the function. If I need to fix a bug, I need to understand how the software works—and I find refactoring is the fastest way to do this. A schedule-driven manager wants me to do things the fastest way I can; how I do it is my responsibility. I’m being paid for my expertise in programming new capabilities fast, and the fastest way is by refactoring—therefore I refactor.” (“Refactoring”, p. 55)

“It may sound like I always recommend refactoring—but there are cases when it’s not worthwhile.” (“Refactoring”, p. 55)

“If I run across code that is a mess, but I don’t need to modify it, then I don’t need to refactor it. Some ugly code that I can treat as an API may remain ugly. It’s only when I need to understand how it works that refactoring gives me any benefit.” (“Refactoring”, p. 55)

“Another case is when it’s easier to rewrite it than to refactor it.” (“Refactoring”, p. 55)

“Whenever anyone advocates for some technique, tool, or architecture, I always look for problems. Few things in life are all sunshine and clear skies. You need to understand the tradeoffs to decide when and where to apply something. I do think refactoring is a valuable technique—one that should be used more by most teams.” (“Refactoring”, p. 55)

“The whole purpose of refactoring is to make us program faster, producing more value with less effort.” (“Refactoring”, p. 56)

“Conversely, I’m more likely to not refactor if it’s part of the code I rarely touch and the cost of the inconvenience isn’t something I feel very often.” (“Refactoring”, p. 56)

“Still, the evidence I hear from my colleagues in the industry is that too little refactoring is far more prevalent than too much.” (“Refactoring”, p. 56)

“We refactor because it makes us faster—faster to add features, faster to fix bugs. It’s important to keep that in front of your mind and in front of communication with others.” (“Refactoring”, p. 57)

“With CI, each team member integrates with mainline at least once per day. This prevents any branches diverting too far from each other and thus greatly reduces the complexity of merges.” (“Refactoring”, p. 58)

“CI doesn’t come for free: It means you use practices to ensure the mainline is healthy, learn to break large features into smaller chunks, and use feature toggles (aka feature flags) to switch off any in-process features that can’t be broken down.” (“Refactoring”, p. 58)

“CI and refactoring work well together, which is why Kent Beck combined them in Extreme Programming.” (“Refactoring”, p. 59)

“’m not saying that you should never use feature branches. If they are sufficiently short, their problems are much reduced. (Indeed, users of CI usually also use branches, but integrate them with mainline each day.)” (“Refactoring”, p. 59)

“This also answers those who are concerned that refactoring carries too much risk of introducing bugs. Without self-testing code, that’s a reasonable worry—which is why I put so much emphasis on having solid tests.” (“Refactoring”, p. 59)

“Legacy Code” (“Refactoring”, p. 60)

“Most people would regard a big legacy as a Good Thing—but that’s one of the cases where programmers’ view is different. Legacy code is often complex, frequently comes with poor tests, and, above all, is written by Someone Else (shudder).” (“Refactoring”, p. 60)

“Refactoring can be a fantastic tool to help understand a legacy system. Functions with misleading names can be renamed so they make sense, awkward programming constructs smoothed out, and the program turned from a rough rock to a polished gem. But the dragon guarding this happy tale is the common lack of tests. If you have a big legacy system with no tests, you can’t safely refactor it into clarity.” (“Refactoring”, p. 60)

“There’s no simple route to dealing with this. The best advice I can give is to get a copy of Working Effectively with Legacy Code [Feathers] and follow its guidance.” (“Refactoring”, p. 60)

“To summarize crudely, it advises you to get the system under test by finding seams in the program where you can insert tests.” (“Refactoring”, p. 60)

“If all this sounds difficult, that’s because it is. Sadly, there’s no shortcut to getting out of a hole this deep—which is why I’m such a strong proponent of writing self-testing code from the start.” (“Refactoring”, p. 60)

“Even when I do have tests, I don’t advocate trying to refactor a complicated legacy mess into beautiful code all at once. What I prefer to do is tackle it in relevant pieces. Each time I pass through a section of the code, I try to make it a little bit better—again, like leaving a camp site cleaner than when I found it.” (“Refactoring”, p. 61)

“My colleague Pramod Sadalage developed an approach to evolutionary database design [mf-evodb] and database refactoring [Ambler & Sadalage] that is now widely used. The essence of the technique is to combine the structural changes to a database’s schema and access code with data migration scripts that can easily compose to handle large changes.” (“Refactoring”, p. 61)

“One difference from regular refactorings is that database changes often are best separated over multiple releases to production. This makes it easy to reverseany change that causes a problem in production. So, when renaming a field, myfirst commit would add the new database field but not use it. I may then set upthe updates so they update both old and new fields at once. I can then graduallymove the readers over to the new field. Only once they have all moved to thenew field, and I’ve given a little time for any bugs to show themselves, would I remove the now-unused old field. This approach to database changes is anexample of a general approach of parallel change [mf-pc] (also called expandcontract).” (“Refactoring”, p. 61)

“parallel change [mf-pc] (also called expand-contract).” (“Refactoring”, p. 61)

“Refactoring has profoundly changed how people think about software architecture.Early in my career, I was taught that software design and architecture wassomething to be worked on, and mostly completed, before anyone started writingcode. Once the code was written, its architecture was fixed and could only decaydue to carelessness.” (“Refactoring”, p. 62)

“The real impact of refactoring on architecture is in how it can be used to forma well-designed code base that can respond gracefully to changing needs. The biggest issue with finishing architecture before coding is that such an approach assumes the requirements for the software can be understood early on. But experience shows that this is often, even usually, an unachievable goal. Repeatedly,I saw people only understand what they really needed from software once they’d had a chance to use it, and saw the impact it made to their work.” (“Refactoring”, p. 62)

“I can happily include mechanisms that don’t increase complexity (such as small, well-named functions) but any flexibility that complicates the software has toprove itself before I include it. If I don’t have different values for a parameterfrom the callers, I don’t add it to the parameter list” (“Refactoring”, p. 62)

“This approach to design goes under various names: simple design, incrementaldesign, or yagni [mf-yagni] (originally an acronym for “you aren’t going to need it”). Yagni doesn’t imply that architectural thinking disappears, although it issometimes naively applied that way. I think of yagni as a different style of incor-porating architecture and design into the development process—a style that isn’tcredible without the foundation of refactoring.” (“Refactoring”, p. 63)

“Adopting yagni doesn’t mean I neglect all upfront architectural thinking. Thereare still cases where refactoring changes are difficult and some preparatory thinking can save time. But the balance has shifted a long way—I’m much moreinclined to deal with issues later when I understand them better. All this has ledto a growing discipline of evolutionary architecture [Ford et al.] where architectsexplore the patterns and practices that take advantage of our ability to iterateover architectural decisions.” (“Refactoring”, p. 63)

“All this has ledto a growing discipline of evolutionary architecture [Ford et al.] where architectsexplore the patterns and practices that take advantage of our ability to iterateover architectural decisions.” (“Refactoring”, p. 63)

“If you’ve read the earlier section on problems, one lesson you’ve probably drawnis that the effectiveness of refactoring is tied to other software practices that ateam uses. Indeed, refactoring’s early adoption was as part of Extreme Program-ming [mf-xp] (XP), a process which was notable for putting together a set ofrelatively unusual and interdependent practices—such as continuous integra-tion, self-testing code, and refactoring (the latter two woven into test-drivendevelopment).” (“Refactoring”, p. 63)

“To refactor on a team, it’s important that each member can refactor when they need to without interfering with others’ work. This is why I encourage Continuous Integration. With CI, each member’s refactoring efforts are quickly shared withtheir colleagues. No one ends up building new work on interfaces that are being removed, and if the refactoring is going to cause a problem with someone else’s work, we know about this quickly.” (“Refactoring”, p. 63)

“With this trio of practices in place, we enable the Yagni design approach thatI talked about in the previous section. Refactoring and yagni positively reinforceeach other: Not just is refactoring (and its prerequisites) a foundation foryagni—yagni makes it easier to do refactoring. This is because it’s easier to changea simple system than one that has lots of speculative flexibility included. Balancethese practices, and you can get into a virtuous circle with a code base thatresponds rapidly to changing needs and is reliable.” (“Refactoring”, p. 64)

“Stated like this, it all sounds rather simple—but in practice it isn’t. Software development, whatever the approach, is a tricky business, with complex interactions between people and machines.” (“Refactoring”, p. 64)

“Refactoring can certainly make soft-ware go more slowly—but it also makes the software more amenable to perfor-mance tuning. The secret to fast software, in all but hard real-time contexts, isto write tunable software first and then tune it for sufficient speed.” (“Refactoring”, p. 64)

“I had speculated with various members of the team (Kent and Martin deny participating in the speculation) on what was likely wrong with code weknew very well. We had even sketched some designs for improvementswithout first measuring what was going on.We were completely wrong. Aside from having a really interestingconversation, we were doing no good at all.The lesson is: Even if you know exactly what is going on in your system,measure performance, don’t speculate. You’ll learn something, and nine timesout of ten, it won’t be that you were right!— Ron Jeffries” (“Refactoring”, p. 66)

“I begin by running the program under a profiler that monitors the program and tells me where it is consuming time and space. This way I can find that small part of the program where the performance hot spots lie. I then focus on thoseperformance hot spots using the same optimizations I would use in the constant-attention approach. But since I’m focusing my attention on a hot spot, I’m getting much more effect with less work. Even so, I remain cautious. As in refactoring,I make the changes in small steps. After each step I compile, test, and rerunthe profiler. If I haven’t improved performance, I back out the change. Icontinue the process of finding and removing hot spots until I get the performancethat satisfies my users.” (“Refactoring”, p. 66)

“I’ve found that refactoring helps me write fast software. It slows the softwarein the short term while I’m refactoring, but makes it easier to tune duringoptimization. I end up well ahead.” (“Refactoring”, p. 67)

“Where Did Refactoring Come From?I’ve not succeeded in pinning down the birth of the term “refactoring.” Goodprogrammers have always spent at least some time cleaning up their code. Theydo this because they have learned that clean code is easier to change than complex and messy code, and good programmers know that they rarely write clean code the first time around.” (“Refactoring”, p. 67)

“Two of the first peopleto recognize the importance of refactoring were Ward Cunningham and KentBeck, who worked with Smalltalk from the 1980s onward” (“Refactoring”, p. 67)

“Bill’s doctoral research looked at refactoring from a toolbuilder’s perspective. Bill was interested in refactorings that would be useful for C++ framework development; he researched the necessary semantics-preserving refactorings and showed how to prove they were semantics-preserving and howa tool could implement these ideas. Bill’s doctoral thesis [Opdyke] was the first substantial work on refactoring.” (“Refactoring”, p. 67)

“And me? I’d always been inclined to clean code, but I’d never considered it tobe that important. Then, I worked on a project with Kent and saw the way he used refactoring. I saw the difference it made in productivity and quality. Thatexperience convinced me that refactoring was a very important technique.” (“Refactoring”, p. 68)

“One downside of this popularity has beenpeople using “refactoring” loosely, to mean any kind of restructuring.” (“Refactoring”, p. 68)

“A technology that’s currently gaining momentum is Language Servers [langserver]: software that will form a syntax tree and present an API to texteditors. Such language servers can support many text editors and providecommands to do sophisticated code analysis and refactoring operations” (“Refactoring”, p. 70)

“Bill Wake’s Refactoring Workbook [Wake]” (“Refactoring”, p. 70)

“Refactoring to Patterns [Kerievsky],” (“Refactoring”, p. 70)

“Refactoring Databases [Ambler & Sadalage] (” (“Refactoring”, p. 70)

“Working Effectively with Legacy Code [Feathers],” (“Refactoring”, p. 70)

““If it stinks, change it.”— Grandma Beck, discussing child-rearing philosophy” (“Refactoring”, p. 71)

“Now comes the dilemma. It is easy to explain how to delete an instance variable or create a hierarchy. These are simple matters. Trying to explain when you shoulddo these things is not so cut-and-dried. Instead of appealing to some vague notion of programming aesthetics (which, frankly, is what we consultants usually do), Iwanted something a bit more solid” (“Refactoring”, p. 71)

“We are switching over to “we” in this chapter to reflect the factthat Kent and I wrote this chapter jointly. You can tell the difference because thefunny jokes are mine and the others are his.” (“Refactoring”, p. 71)

“Mysterious Name” (“Refactoring”, p. 72)

“Puzzling over some text to understand what’s going on is a great thing if you’rereading a detective novel, but not when you’re reading code. We may fantasizeabout being International Men of Mystery, but our code needs to be mundane and clear. One of the most important parts of clear code is good names, so we put a lot of thought into naming functions, modules, variables, classes, so theyclearly communicate what they do and how to use them.” (“Refactoring”, p. 72)

“Renaming is not just an exercise in changing names. When you can’t think ofa good name for something, it’s often a sign of a deeper design malaise. Puzzling over a tricky name has often led us to significant simplifications to our code.” (“Refactoring”, p. 72)

“Duplicated CodeIf you see the same code structure in more than one place, you can be sure thatyour program will be better if you find a way to unify them. Duplication meansthat every time you read these copies, you need to read them carefully to see ifthere’s any difference. If you need to change the duplicated code, you have tofind and catch each duplication.” (“Refactoring”, p. 72)

“The net effect is that you should be much more aggressive about decomposingfunctions. A heuristic we follow is that whenever we feel the need to commentsomething, we write a function instead. Such a function contains the code thatwe wanted to comment but is named after the intention of the code rather thanthe way it works. We may do this on a group of lines or even on a single line ofcode. We do this even if the method call is longer than the code it replaces—provided the method name explains the purpose of the code. The key here isnot function length but the semantic distance between what the method doesand how it does it.” (“Refactoring”, p. 73)

“How do you identify the clumps of code to extract? A good technique is tolook for comments. They often signal this kind of semantic distance. A block ofcode with a comment that tells you what it is doing can be replaced by a methodwhose name is based on the comment. Even a single line is worth extracting ifit needs explanation.” (“Refactoring”, p. 73)

“Long Parameter List In our early programming days, we were taught to pass in as parameters every-thing needed by a function. This was understandable because the alternative wasglobal data, and global data quickly becomes evil. But long parameter lists areoften confusing in their own right.” (“Refactoring”, p. 74)

“Global DataSince our earliest days of writing software, we were warned of the perils of global data—how it was invented by demons from the fourth plane of hell, whichis the resting place of any programmer who dares to use it. And, although weare somewhat skeptical about fire and brimstone, it’s still one of the most pungent odors we are likely to run into.” (“Refactoring”, p. 74)

“Global data illustrates Paracelsus’s maxim: The difference between a poison and something benign is the dose. You can get away with small doses of global data, but it gets exponentially harder to deal with the more you have. Even with little bits, we like to keep it encapsulated—that’s the key to coping with changesas the software evolves.” (“Refactoring”, p. 75)

“Mutable DataChanges to data can often lead to unexpected consequences and tricky bugs. I can update some data here, not realizing that another part of the software expectssomething different and now fails—a failure that’s particularly hard to spot if itonly happens under rare conditions” (“Refactoring”, p. 75)

“Divergent ChangeWe structure our software to make change easier; after all, software is meant tobe soft. When we make a change, we want to be able to jump to a single clear point in the system and make the change. When you can’t do this, you aresmelling one of two closely related pungencies.” (“Refactoring”, p. 76)

“The database interaction and financial processing problemsare separate contexts, and we can make our programming life better by moving such contexts into separate modules. That way, when we have a change to onecontext, we only have to understand that one context and ignore the other. Wealways found this to be important, but now, with our brains shrinking with age, it becomes all the more imperative. Of course, you often discover this only afteryou’ve added a few databases or financial instruments; context boundaries areusually unclear in the early days of a program and continue to shift as a softwaresystem’s capabilities change.” (“Refactoring”, p. 76)

“Shotgun SurgeryShotgun surgery is similar to divergent change but is the opposite. You whiff this when, every time you make a change, you have to make a lot of little edits to a” (“Refactoring”, p. 76)

“lot of different classes. When the changes are all over the place, they are hardto find, and it’s easy to miss an important change.” (“Refactoring”, p. 77)

“A useful tactic for shotgun surgery is to use inlining refactorings, such as InlineFunction (115) or Inline Class (186), to pull together poorly separated logic. You’ll end up with a Long Method or a Large Class, but can then use extractions tobreak it up into more sensible pieces. Even though we are inordinately fond ofsmall functions and classes in our code, we aren’t afraid of creating something large as an intermediate step to reorganization.” (“Refactoring”, p. 77)

“Feature EnvyWhen we modularize a program, we are trying to separate the code into zonesto maximize the interaction inside a zone and minimize interaction betweenzones. A classic case of Feature Envy occurs when a function in one modulespends more time communicating with functions or data inside another mod-ule than it does within its own module.” (“Refactoring”, p. 77)

“Data items tend to be like children: They enjoy hanging around together. Often,you’ll see the same three or four data items together in lots of places: as fieldsin a couple of classes, as parameters in many method signatures. Bunches of datathat hang around together really ought to find a home together.” (“Refactoring”, p. 78)

“You’ll notice that we advocate creating a class here, not a simple record structure. We do this because using a class gives you the opportunity to make a niceperfume. You can now look for cases of feature envy, which will suggest behaviorthat can be moved into your new classes. We’ve often seen this as a powerfuldynamic that creates useful classes and can remove a lot of duplication and accelerate future development, allowing the data to become productive membersof society.” (“Refactoring”, p. 78)

“We find many programmers are curiouslyreluctant to create their own fundamental types which are useful for theirdomain—such as money, coordinates, or ranges” (“Refactoring”, p. 78)

“Strings are particularly common petri dishes for this kind of odor: A telephone number is more than just a collection of characters. If nothing else, a proper typecan often include consistent display logic for when it needs to be displayed in auser interface. Representing such types as strings is such a common stench thatpeople call them “stringly typed” variables.” (“Refactoring”, p. 78)

“Repeated SwitchesTalk to a true object-oriented evangelist and they’ll soon get onto the evils ofswitch statements. They’ll argue that any switch statement you see is begging forReplace Conditional with Polymorphism (272). We’ve even heard some people argue that all conditional logic should be replaced with polymorphism, tossing mostifs into the dustbin of history.” (“Refactoring”, p. 79)

“Lazy ElementWe like using program elements to add structure—providing opportunities forvariation, reuse, or just having more helpful names. But sometimes the structureisn’t needed.” (“Refactoring”, p. 80)

“Speculative GeneralityBrian Foote suggested this name for a smell to which we are very sensitive. Youget it when people say, “Oh, I think we’ll need the ability to do this kind of thingsomeday” and thus add all sorts of hooks and special cases to handle things thataren’t required. The result is often harder to understand and maintain. If all this machinery were being used, it would be worth it. But if it isn’t, it isn’t. The ma-chinery just gets in the way, so get rid of it” (“Refactoring”, p. 80)

“Temporary FieldSometimes you see a class in which a field is set only in certain circumstances. Such code is difficult to understand, because you expect an object to need all of its fields. Trying to understand why a field is there when it doesn’t seem to beused can drive you nuts.” (“Refactoring”, p. 80)

“Message ChainsYou see message chains when a client asks one object for another object, which the client then asks for yet another object, which the client then asks for yet an-other another object, and so on. You may see these as a long line of getThismethods, or as a sequence of temps. Navigating this way means the client iscoupled to the structure of the navigation. Any change to the intermediaterelationships causes the client to have to change.” (“Refactoring”, p. 81)

“Middle Man” (“Refactoring”, p. 81)

“However, this can go too far. You look at a class’s interface and find half the methods are delegating to this other class.” (“Refactoring”, p. 81)

“Insider TradingSoftware people like strong walls between their modules and complain bitterly about how trading data around too much increases coupling. To make things work, some trade has to occur, but we need to reduce it to a minimum and keepit all above board.” (“Refactoring”, p. 82)

“Large ClassWhen a class is trying to do too much, it often shows up as too many fields. Whena class has too many fields, duplicated code cannot be far behind.” (“Refactoring”, p. 82)

“Alternative Classes with Different InterfacesOne of the great benefits of using classes is the support for substitution, allow-ing one class to swap in for another in times of need. But this only works if theirinterfaces are the same.” (“Refactoring”, p. 83)

“Data ClassThese are classes that have fields, getting and setting methods for the fields, andnothing else. Such classes are dumb data holders and are often being manipulatedin far too much detail by other classes.” (“Refactoring”, p. 83)

“Data classes are often a sign of behavior in the wrong place, which means youcan make big progress by moving it from the client into the data class itself. Butthere are exceptions, and one of the best exceptions is a record that’s being usedas a result record from a distinct function invocation. A good example of this is the intermediate data structure after you’ve applied Split Phase (154).” (“Refactoring”, p. 83)

“Refused BequestSubclasses get to inherit the methods and data of their parents. But what if they don’t want or need what they are” (“Refactoring”, p. 83)

“given? They are given all these great gifts andpick just a few to play with.The traditional story is that this means the hierarchy is wrong.” (“Refactoring”, p. 83)

“Often, you’ll hear advice that all superclasses should be abstract.” (“Refactoring”, p. 83)

“You’ll guess from our snide use of “traditional” that we aren’t going to advise this—at least not all the time. We do subclassing to reuse a bit of behavior allthe time, and we find it a perfectly good way of doing business.” (“Refactoring”, p. 84)

“The smell of refused bequest is much stronger if the subclass is reusing behaviorbut does not want to support the interface of the superclass. We don’t mind refusing implementations—but refusing interface gets us on our high horses.” (“Refactoring”, p. 84)

“CommentsDon’t worry, we aren’t saying that people shouldn’t write comments. In our olfac-tory analogy, comments aren’t a bad smell; indeed they are a sweet smell. Thereason we mention comments here is that comments are often used as a deodor-ant. It’s surprising how often you look at thickly commented code and notice that the comments are there because the code is bad.” (“Refactoring”, p. 84)

“When you feel the need to write a comment, first try torefactor the code so that anycomment becomes superfluous.” (“Refactoring”, p. 84)

“A good time to use a comment iswhen you don’t know what to do. Inaddition to describing what is going on,comments can indicate areas in whichyou aren’t sure. A comment can also ex-plain why you did something. This kindof information helps future modifiers,especially forgetful ones.” (“Refactoring”, p. 84)

“The Value of Self-Testing CodeIf you look at how most programmers spend their time, you’ll find that writingcode is actually quite a small fraction. Some time is spent figuring out what oughtto be going on, some time is spent designing, but most time is spent debugging.I’m sure every reader can remember long hours of debugging—often, well intothe night. Every programmer can tell a story of a bug that took a whole day (ormore) to find. Fixing the bug is usually pretty quick, but finding it is a nightmare.And then, when you do fix a bug, there’s always a chance that another one willappear and that you might not even notice it till much later. And you’ll spend ages finding that bug.” (“Refactoring”, p. 85)

“Make sure all tests are fully automatic and that they checktheir own results.” (“Refactoring”, p. 86)

“A suite of tests is a powerful bug detector that decapitatesthe time it takes to find bugs.” (“Refactoring”, p. 86)

“While flying fromSwitzerland to Atlanta for OOPSLA 1997,Kent Beck paired with Erich Gamma toport his unit testing framework fromSmalltalk to Java. The resulting framework, called JUnit, has been enormously influential for program testing, inspiring a huge variety of similar tools [mf-xunit]in lots of different languages.” (“Refactoring”, p. 86)

“Admittedly, it is not so easy to persuade others to follow this route. Writingthe tests means a lot of extra code to write. Unless you have actually experiencedhow it speeds programming, self-testing does not seem to make sense.” (“Refactoring”, p. 86)

“In fact, one of the most useful times to write tests is before I start programming.When I need to add a feature, I begin by writing the test. This isn’t as backwardas it sounds. By writing the test, I’m asking myself what needs to be done to add the function. Writing the test also concentrates me on the interface rather than theimplementation (always a good thing). It also means I have a clear point at whichI’m done coding—when the test works” (“Refactoring”, p. 86)

“Kent Beck baked this habit of writing the test first into a technique called Test-Driven Development (TDD) [mf-tdd]. The Test-Driven Development approachto programming relies on short cycles of writing a (failing) test, writing the code tomake that test work, and refactoring to ensure the result is as clean as possible.This test-code-refactor cycle should occur many times per hour, and can be avery productive and calming way to write code. I’m not going to discuss it furtherhere, but I do use and warmly recommend it.” (“Refactoring”, p. 87)

“Kent” (“Refactoring”, p. 87)

“book is aboutrefactoring. Refactoring requires tests. If you want to refactor, you have to writetests.” (“Refactoring”, p. 87)

“When I develop code, I write the tests as I go. But sometimes, I need to refactor some code without tests—then I have to make the code self-testing beforeI begin.” (“Refactoring”, p. 87)

“Always make sure a test willfail when it should.” (“Refactoring”, p. 91)

“I’m always nervous that a test isn’t reallyexercising the code the way I think it is, and thus won’t catch a bug when I needit to. So I like to see every test fail at least once when I write it. My favorite wayof doing that is to temporarily inject a fault into the code” (“Refactoring”, p. 91)

“Run tests frequently. Run those exercising the code you’reworking on at least every fewminutes; run all tests at leastdaily.” (“Refactoring”, p. 92)

“Now I’ll continue adding more tests. The style I follow is to look at all the things the class should do and test each one of them for any conditions that mightcause the class to fail. This is not the same as testing every public method, whichis what some programmers advocate. Testing should be risk-driven; remember,I’m trying to find bugs, now or in the future” (“Refactoring”, p. 93)

“I get many benefits from testing even if I do only a little testing.My focus is to test the areas that I’m most worried about going wrong. That way I get the most benefit for my testing effort” (“Refactoring”, p. 93)

“It is better to write and runincomplete tests than not torun complete tests.” (“Refactoring”, p. 93)

“it introduces a petri dish that’s primed for one of the nastiest bugs in testing—ashared fixture which causes tests to interact.” (“Refactoring”, p. 94)

“I take the initial standard fixture that’s set up bythe beforeEach block, I exercise that fixture for the test, then I verify the fixture hasdone what I think it should have done. If you read much about testing, you’ll hear these phases described variously as setup-exercise-verify, given-when-then,or arrange-act-assert” (“Refactoring”, p. 95)

“Asa general rule, it’s wise to have only a single verify statement in each it clause. This is because the test will fail on the first verification failure—which can oftenhide useful information when you’re figuring out why a test is broken.” (“Refactoring”, p. 96)

“Think of the boundary condi-tions under which things mightgo wrong and concentrate yourtests there.” (“Refactoring”, p. 97)

“Don’t let the fear that testingcan’t catch all bugs stop youfrom writing tests that catchmost bugs” (“Refactoring”, p. 98)

“When do you stop? I’m sure you haveheard many times that you cannot provethat a program has no bugs by testing.That’s true, but it does not affect theability of testing to speed up program-ming.” (“Refactoring”, p. 98)

“is a law of diminishing returnsin testing, and there is the danger that by trying to write too many tests you” (“Refactoring”, p. 98)

“become discouraged and end up not writing any.” (“Refactoring”, p. 99)

“You should concentrate onwhere the risk is. Look at the code and see where it becomes complex. Look ata function and consider the likely areas of error. Your tests will not find every bug, but as you refactor, you will understand the program better and thus find more bugs. Although I always start refactoring with a test suite, I invariably addto it as I go along.” (“Refactoring”, p. 99)

“That’s as far as I’m going to go with this chapter—after all, this is a book onrefactoring, not on testing. But testing is an important topic, both because it’s anecessary foundation for refactoring and because it’s a valuable tool in its ownright. While I’ve been happy to see the growth of refactoring as a programmingpractice since I wrote this book, I’ve been even happier to see the change in atti-tudes to testing. Previously seen as the responsibility of a separate (and inferior)group, testing is now increasingly a first-class concern of any decent softwaredeveloper. Architectures often are, rightly, judged on their testability.” (“Refactoring”, p. 99)

“Architectures often are, rightly, judged on their testability” (“Refactoring”, p. 99)

“Unless youare either very skilled or very lucky, you won’t get your tests right the first time. I find I’m constantly working on the test suite—just as much as I work on themain code.” (“Refactoring”, p. 99)

“An important habit to get into is to respond to a bug by firstwriting a test that clearly reveals the bug. Only after I have the test do I fix thebug. By having the test, I know the bug will stay dead. I also think about that bug and its test: Does it give me clues to other gaps in the test suite?” (“Refactoring”, p. 99)

“When you get a bug report,start by writing a unit test thatexposes the bug.” (“Refactoring”, p. 99)

“It is possible to write too many tests. One sign of that is when I spend more time changing the tests than the code under test—and I feel the tests are slowingme down. But while over-testing does happen, it’s vanishingly rare compared tounder-testing” (“Refactoring”, p. 100)

“The argument that makes most sense to me, however, isthe separation between intention and implementation. If you have to spend effortlooking at a fragment of code and figuring out what it’s doing, then you shouldextract it into a function and name the function after the “what.”” (“Refactoring”, p. 107)

“Once I accepted this principle, I developed a habit of writing very smallfunctions—typically, only a few lines long. To me, any function with more thanhalf-a-dozen lines of code starts to smell, and it’s not unusual for me to havefunctions that are a single line of code” (“Refactoring”, p. 107)

“The fact that size isn’t important wasbrought home to me by an example that Kent Beck showed me from the original Smalltalk system. Smalltalk in those days ran on black-and-white systems. If you wanted to highlight some text or graphics, you would reverse the video. Smalltalk’sgraphics class had a method for this called highlight, whose implementation wasjust a call to the method reverse. The name of the method was longer than its implementation—but that didn’t matter because there was a big distance between the intention of the code and its implementation.” (“Refactoring”, p. 107)

“Some people are concerned about short functions because they worry aboutthe performance cost of a function call. When I was young, that was occasionallya factor, but that’s very rare now. Optimizing compilers often work better withshorter functions which can be cached more easily. As always, follow the generalguidelines on performance optimization.” (“Refactoring”, p. 107)

“Small functions like this only work if the names are good, so you need to paygood attention to naming.” (“Refactoring”, p. 107)

“Create a new function, and name it after the intent of the function (name it by what it does, not by how it does it).” (“Refactoring”, p. 107)

“You may be wondering what the Clock.today is about. It is a Clock Wrapper [mf-cw]—an objectthat wraps calls to the system clock. I avoid putting direct calls to things like Date.now() in my code, because it leads to nondeterministic tests and makes it difficult to reproduce error conditions when diagnosing failures.” (“Refactoring”, p. 109)

“At this point you may be wondering, “What happens if more than one variableneeds to be returned?”Here, I have several options. Usually I prefer to pick different code to extract.I like a function to return one value, so I would try to arrange for multiple functions for the different values. If I really need to extract with multiple values, Ican form a record and return that—but usually I find it better to rework thetemporary variables instead. Here I like using Replace Temp with Query (178) andSplit Variable (240).” (“Refactoring”, p. 114)

“some-times, I do come across a function in which the body is as clear as the name. Or,I refactor the body of the code into something that is just as clear as the name.When this happens, I get rid of the function. Indirection can be helpful, butneedless indirection is irritating.” (“Refactoring”, p. 115)

“I commonly use Inline Function when I see code that’s using too muchindirection—when it seems that every function does simple delegation to anotherfunction, and I get lost in all the delegation. Some of this indirection may be worthwhile, but not all of it. By inlining, I can flush out the useful ones and eliminate the rest.” (“Refactoring”, p. 115)

“Written this way, Inline Function is simple. In general, it isn’t. I could writepages on how to handle recursion, multiple return points, inlining a method intoanother object when you don’t have accessors, and the like. The reason I don’t is that if you encounter these complexities, you shouldn’t do this refactoring.” (“Refactoring”, p. 116)

“The most important element of such a joint is the name of the function. Agood name allows me to understand what the function does when I see it called,without seeing the code that defines its implementation. However, coming up withgood names is hard, and I rarely get my names right the first time. When I finda name that’s confused me, I’m tempted to leave it—after all, it’s only a name. This is the work of the evil demon Obfuscatis; for the sake of my program’s soulI must never listen to him. If I see a function with the wrong name, it is imperative that I change it as soon as I understand what a better name could be” (“Refactoring”, p. 124)

“Often, a good way to improve a name is to write a comment to describethe function’s purpose, then turn that comment into a name” (“Refactoring”, p. 125)

“The only right answer to this puzzle is that there is no right answer, especiallyover time. So I find it’s essential to be familiar with Change Function Declarationso the code can evolve with my understanding of what the best joints in the codeneed to be.” (“Refactoring”, p. 125)

“Refactoring is all about manipulating the elements of our programs. Data is more awkward to manipulate than functions.” (“Refactoring”, p. 132)

“If I move data around, I have to change all the references to the data in a single cycle to keep the code working.” (“Refactoring”, p. 132)

“So if I want to move widely accessed data, often the best approach is to first encapsulate it by routing all its access through functions. That way, I turn the difficult task of reorganizing data into the simpler task of reorganizing functions.” (“Refactoring”, p. 132)

“Encapsulating data is valuable for other things too. It provides a clear point to monitor changes and use of the data; I can easily add validation or consequential logic on the updates. It is my habit to make all mutable data encapsulated like this and only accessed through functions if its scope is greater than a single function.” (“Refactoring”, p. 132)

“My approach with legacy code is that whenever I need to change or add a new reference to such a variable, I should take the opportunity to encapsulate it. That way I prevent the increase of coupling to commonly used data.” (“Refactoring”, p. 133)

“A common convention in JavaScript is to name a getting function and setting function the same and differentiate them due the presence of an argument. I call this practice Overloaded Getter Setter [mf-ogs] and strongly dislike it. So, even though I don’t like the get prefix, I will keep the set prefix.” (“Refactoring”, p. 134)

“For this, I have a couple of options. The simplest one is to prevent any changes to the value. My favorite way to handle this is by modifying the getting function to return a copy of the data.” (“Refactoring”, p. 135)

“Naming things well is the heart of clear programming. Variables can do a lot to explain what I’m up to—if I name them well.” (“Refactoring”, p. 137)

“I could continue by inlining the wrapping functions so all callers are using the variable directly. But I’d rarely want to do this. If the variable is used widely enough that I feel the need to encapsulate it in order to change its name, it’s worth keeping it encapsulated behind functions for the future.” (“Refactoring”, p. 138)

“I often see groups of data items that regularly travel together, appearing infunction after function. Such a group is a data clump, and I like to replace it witha single data structure.” (“Refactoring”, p. 140)

“Grouping data into a structure is valuable because it makes explicit the relationship between the data items” (“Refactoring”, p. 140)

“But the real power of this refactoring is how it enables deeper changes to thecode. When I identify these new structures, I can reorient the behavior ofthe program to use these structures.” (“Refactoring”, p. 140)

“That completes this refactoring. However, replacing a clump of parameterswith a real object is just the setup for the really good stuff. The great benefits ofmaking a class like this is that I can then move behavior into the new class” (“Refactoring”, p. 143)

“When I see a group of functions that operate closely together on a commonbody of data (usually passed as arguments to the function call), I see an opportunity to form a class.” (“Refactoring”, p. 144)

“In addition to organizing already formed functions, this refactoring also providesa good opportunity to identify other bits of computation and refactor them into methods on the new class.” (“Refactoring”, p. 144)

“In general, I prefer immutable data, but manycircumstances force us to work with mutable data” (“Refactoring”, p. 148)

“Software often involves feeding data into programs that calculate various derived information from it. These derived values may be needed in several places, andthose calculations are often repeated wherever the derived data is used. I preferto bring all of these derivations together, so I have a consistent place to find andupdate them and avoid any duplicate logic.” (“Refactoring”, p. 149)

“One way of dealing with this is to move all of these derivations into a transfor-mation step that takes the raw reading and emits a reading enriched with all thecommon derived results.” (“Refactoring”, p. 151)

“When I’m applying a transformation that produces essentially the same thingbut with additional information, I like to name it using “enrich”. If it were producing something I felt was different, I would name it using “transform”.” (“Refactoring”, p. 151)

“When I run into code that’s dealing with two different things, I look for a wayto split it into separate modules. I endeavor to make this split because, if I need tomake a change, I can deal with each topic separately and not have to hold bothin my head together.” (“Refactoring”, p. 154)

“The most obvious example of this is a compiler. It’s a basic task is to take sometext (code in a programming language) and turn it into some executable form(e.g., object code for a specific hardware). Over time, we’ve found this can beusefully split into a chain of phases: tokenizing the text, parsing the tokens intoa syntax tree, then various steps of transforming the syntax tree (e.g., for optimization), and finally generating the object code. Each step has a limited scopeand I can think of one step without understanding the details of others.” (“Refactoring”, p. 155)

“Splitting phases like this is common in large software; the various phases in a compiler can each contain many functions and classes. But I can carry out thebasic split-phase refactoring on any fragment of code—whenever I see an opportunity to usefully separate the code into different phases.” (“Refactoring”, p. 155)

“Perhaps the most important criteria to be used in decomposing modules is toidentify secrets that modules should hide from the rest of the system [Parnas].” (“Refactoring”, p. 161)

“I like encapsulating any mutable data in my programs. This makes it easier to see when and how data structures are modified, which then makes it easier to change those data structures when I need to” (“Refactoring”, p. 170)

“Access to a collection variable may be encapsulated, but if the getter returns the collection itself, then that collection’s membership can be altered without the enclosing class being able to intervene.” (“Refactoring”, p. 170)

“Another difference between using a proxy and a copy is that a modification of the source data will be visible in the proxy but not in a copy. This isn’t an issue most of the time, because lists accessed in this way are usually only held for a short time. What’s important here is consistency within a code base. Use only one mechanism so everyone can get used to how it behaves and expect it when calling any collection accessor function.” (“Refactoring”, p. 171)

“This violates encapsulating because the person class has no ability to take control when the list is updated in this way. While the reference to the field is encapsulated, the content of the field is not.” (“Refactoring”, p. 172)

“In general, I find it wise to be moderately paranoid about collections and I’d rather copy them unnecessarily than debug errors due to unexpected modifications.” (“Refactoring”, p. 173)

“As soon as I realize I want to do something other than simple printing, I like to create a new class for that bit of data. At first, such a class does little more than wrap the primitive—but once I have that class, I have a place to put behavior specific to its needs.” (“Refactoring”, p. 174)

“These little values start very humble, but once nurtured they can grow into useful tools. They may not look like much, but I find their effects on a code base can be surprisingly large.” (“Refactoring”, p. 174)

“If I’m working on breaking up a large function, turning variables into their own functions makes it easier to extract parts of the function, since I no longer need” (“Refactoring”, p. 178)

“to pass in variables into the extracted functions.” (“Refactoring”, p. 179)

“You’ve probably read guidelines that a class should be a crisp abstraction, only handle a few clear responsibilities, and so on. In practice, classes grow. You add some operations here, a bit of data there. You add a responsibility to a class feeling that it’s not worth a separate class—but as that responsibility grows and breeds, the class becomes too complicated. Soon, your class is as crisp as a microwaved duck.” (“Refactoring”, p. 182)

“You need to consider where it can be split—and split it. A good sign is when a subset of the data and a subset of the methods seem to go together. Other good signs are subsets of data that usually change together or are particularly dependent on each other.” (“Refactoring”, p. 182)

“One sign that often crops up later in development is the way the class is subtyped. You may find that subtyping affects only a few features or that some features need to be subtyped one way and other features a different way.” (“Refactoring”, p. 182)

“Another reason to use Inline Class is if I have two classes that I want to refactor into a pair of classes with a different allocation of features. I may find it easier to first use Inline Class to combine them into a single class, then Extract Class (182) to make the new separation” (“Refactoring”, p. 186)

“A good encapsulation six months ago may be awkward now. Refactoring means I never have to say I’m sorry—I just fix it.” (“Refactoring”, p. 192)

“I’ve never tried to skin a cat. I’m told there are several ways to do it. I’m sure some are easier than others. So it is with algorithms. If I find a clearer way to do something, I replace the complicated way with the clearer way. Refactoring can break down something complex into simpler pieces, but sometimes I just reach the point at which I have to remove the whole algorithm and replace it with something simpler. This occurs as I learn more about the problem and realize that there’s an easier way to do it. It also happens if I start using a library that supplies features that duplicate my code.” (“Refactoring”, p. 195)

“And then there’s the favorite refactoring of many a fine programmer: Remove Dead Code (237). Nothing is as satisfying as applying the digital flamethrower to superfluous statements.” (“Refactoring”, p. 197)

“The heart of a good software design is its modularity—which is my ability to make most modifications to a program while only having to understand a small part of it. To get this modularity, I need to ensure that related software elements are grouped together and the links between them are easy to find and understand.” (“Refactoring”, p. 198)

“But my understanding of how to do this isn’t static—as I better understand what I’m doing, I learn how to best group together software elements. To reflect that growing understanding, I need to move elements around.” (“Refactoring”, p. 198)

“One of the most straightforward reasons to move a function is when it refer-ences elements in other contexts more than the one it currently resides in.” (“Refactoring”, p. 198)

“In general, I’m wary of nested functions—theytoo easily set up hidden data interrelationships that can get hard to follow.” (“Refactoring”, p. 204)

“Move Statements to Callers works well for small changes, but sometimes theboundaries between caller and callee need complete reworking. In that case, my best move is to use Inline Function (115) and then slide and extract new functions to form better boundaries.” (“Refactoring”, p. 218)

“Many programmers are uncomfortable with this refactoring, as it forces you toexecute the loop twice. My reminder, as usual, is to separate refactoring from optimization (Refactoring and Performance (64)).” (“Refactoring”, p. 228)

“Using a variable fortwo different things is very confusing for the reader.” (“Refactoring”, p. 240)

“that is a collecting variable,so don’t split it. A collecting variable is often used for calculating sums, stringconcatenation, writing to a stream, or adding to a collection.” (“Refactoring”, p. 240)

“ve shown this process in its most heavyweight form needed for a widely useddata structure. If it’s being used only locally, as in a single function, I can probably just rename the various properties in one go without doing encapsulation. It’s amatter of judgment when to apply to the full mechanics here—but, as usual withrefactoring, if my tests break, that’s a sign I need to use the more gradualprocedure.” (“Refactoring”, p. 247)

“One of the biggest sources of problems in software is mutable data. Data changescan often couple together parts of code in awkward ways, with changes in onepart leading to knock-on effects that are hard to spot. In many situations it’s notrealistic to entirely remove mutable data—but I do advocate minimizing the scopeof mutable data at much as possible” (“Refactoring”, p. 248)

“Here’s a small but perfectly formed example of ugliness:” (“Refactoring”, p. 249)

“Ugliness is in the eye of beholder; here, I see ugliness in duplication—not the common duplication of code but duplication of data” (“Refactoring”, p. 249)

“If I treat a field as a value, I can change the class of the inner object to makeit a Value Object [mf-vo].” (“Refactoring”, p. 252)

“This also suggests when I shouldn’t do this refactoring. If I want to share anobject between several objects so that any change to the shared object is visibleto all its collaborators, then I need the shared object to be a reference” (“Refactoring”, p. 252)

“In most object-oriented languages, there is a built-in equality test that is supposed tobe overridden for value-based equality. In Ruby, I can override the == operator; in Java, I override the Object.equals() method. And whenever I override an equality method, I usually need to override a hashcode generating method too (e.g., Object.hashCode() in Java)to ensure collections that use hashing work properly with my new value.” (“Refactoring”, p. 255)

“Exactly where to store entities like this will vary from application to application,but for a simple case I like to use a repository object [mf-repos].” (“Refactoring”, p. 257)

“The repository allows me to register customer objects with an ID and ensuresI only create one customer object with the same ID.” (“Refactoring”, p. 258)

“One problem with this code is that the constructor body is coupled to theglobal repository. Globals should be treated with care—like a powerful drug, theycan be beneficial in small doses but a poison if used too much. If I’m concernedabout it, I can pass the repository as a parameter to the constructor.” (“Refactoring”, p. 258)

“Much of the power of programs comes from their ability to implement conditionallogic—but, sadly, much of the complexity of programs lies in these conditionals.” (“Refactoring”, p. 259)

“One entry point is enforced by modern lan-guages, but one exit point is really not a useful rule. Clarity is the key principle:If the method is clearer with one exit point, use one exit point; otherwise don’t.” (“Refactoring”, p. 267)

“The rule is that you always get an extra strawberry when you remove a mutablevariable” (“Refactoring”, p. 269)

“When I have a function that gives me a value and has no observable side effects,I have a very valuable thing. I can call this function as often as I like. I can movethe call to other places in a calling function. It’s easier to test. In short, I have alot less to worry about.It is a good idea to clearly signal the difference between functions with sideeffects and those without. A good rule to follow is that any function that returnsa value should not have observable side effects—the command-query separation [mf-cqs].” (“Refactoring”, p. 306)

“If I come across a method that returns a value but also has side effects, I always try to separate the query from the modifier.” (“Refactoring”, p. 306)

“If a call passes in a value that the function can just as easily determine for itself, that’s a form of duplication—one that unnecessarily complicates the caller whichhas to determine the value of a parameter when it could be freed from that work.” (“Refactoring”, p. 324)

“y usual habit is tosimplify life for callers, which implies moving responsibility to the functionbody—but only if that responsibility is appropriate there.” (“Refactoring”, p. 324)

“When looking through a function’s body, I sometimes see references to somethingin the function’s scope that I’m not happy with. This might be a reference to aglobal variable, or to an element in the same module that I intend to move away.To resolve this, I need to replace the internal reference with a parameter, shiftingthe responsibility of resolving the reference to the caller of the function” (“Refactoring”, p. 327)

“Most of these cases are due to my wish to alter the dependency relationships in the code—to make the target function no longer dependent on the element Iwant to parameterize. There’s a tension here between converting everything toparameters, which results in long repetitive parameter lists, and sharing a lot ofscope which can lead to a lot of coupling between functions.” (“Refactoring”, p. 327)

“It’s easier to reason about a function that will always give the same result whencalled with same parameter values—this is called referential transparency. If afunction accesses some element in its scope that isn’t referentially transparent,then the containing function also lacks referential transparency” (“Refactoring”, p. 327)

“such a move will shift responsibil-ity to the caller, there is often a lot to be gained by creating clear modules withreferential transparency” (“Refactoring”, p. 328)

“Moving a dependency out of a module pushes the responsibility of dealing with that dependency back to the caller. That’s the trade-off for the reduced coupling.” (“Refactoring”, p. 330)

“Command objects provide a powerful mechanism for handling complex computations. They can easily be broken down into separate methods sharing commonstate through the fields; they can be invoked via different methods for differenteffects; they can have their data built up in stages. But that power comes at acost. Most of the time, I just want to invoke a function and have it do its thing.If that’s the case, and the function isn’t too complex, then a command object ismore trouble than its worth and should be turned into a regular function.” (“Refactoring”, p. 344)

“Like any powerful mechanism, it is both very useful and easy to misuse, and it’s often hard to see the misuse until it’s in the rear-view mirror.” (“Refactoring”, p. 349)

“Whenever there is duplication, there is risk that an alteration to one copy will not be made to the other. Usually, it is difficult to find the duplicates.” (“Refactoring”, p. 350)

“The factory encapsulates the creation of the subclasses, but there is also the use of instanceof—which never smells good.” (“Refactoring”, p. 372)

“But inheritance has its downsides. Most obviously, it’s a card that can only be played once. If I have more than one reason to vary something, I can only use inheritance for a single axis of variation. So, if I want to vary behavior of people by their age category and by their income level, I can either have subclasses for young and senior, or for well-off and poor—I can’t have both.” (“Refactoring”, p. 382)

“There is a popular principle: “Favor object composition over class inheritance” (where composition is effectively the same as delegation). Many people take this to mean “inheritance considered harmful” and claim that we should never use inheritance.” (“Refactoring”, p. 382)

“This usage is actually consistent with the principle—which comes from the Gang of Four book [gof] that explains how inheritance and composition work together. The principle was a reaction to the overuse of inheritance.” (“Refactoring”, p. 382)

“Actually, it isn’t quite as perfect as the previous paragraph implies. There are things in the superclass structure that only make sense due to the subclass—such as methods that have been factored in such a way as to make it easier to override just the right kinds of behavior.” (“Refactoring”, p. 385)

“[Feathers] Michael Feathers. Working Effectively with Legacy Code. Prentice Hall, 2004. ISBN 0131177052.” (“Refactoring”, p. 405)

“[Ford et al.] Neal Ford, Rebecca Parsons, and Patrick Kua. Building Evolutionary Architectures. O’Reilly, 2017. ISBN 1491986360.” (“Refactoring”, p. 405)