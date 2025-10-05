## Straight lines

Mathcha input:

```tikz
\begin{document}
\tikzset{every picture/.style={line width=0.75pt}} %set default line width to 0.75pt        

\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1]
%uncomment if require: \path (0,300); %set diagram left start at 0, and has height of 300

%Straight Lines [id:da42258022865066713] 
\draw    (120,100) -- (220,200) ; 
%Straight Lines [id:da20377336023283854]
\draw [color={rgb, 255:red, 255; green, 0; blue, 0 }  ,draw opacity=1 ]   (100,150) -- (198.59,248.59) ;
\draw [shift={(200,250)}, rotate = 225] [color={rgb, 255:red, 255; green, 3; blue, 33 }  ,draw opacity=1 ][line width=0.75]    (10.93,-3.29) .. controls (6.95,-1.4) and (3.31,-0.3) .. (0,0) .. controls (3.31,0.3) and (6.95,1.4) .. (10.93,3.29)   ;
%Straight Lines [id:da6853171422293277]
\draw [color={rgb, 255:red, 0; green, 0; blue, 255 }  ,draw opacity=1 ]   (210,130) -- (307.88,227.88) ;
\draw [shift={(310,230)}, rotate = 225] [fill={rgb, 255:red, 0; green, 0; blue, 255 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle    ;
%Straight Lines [id:da6253093591230833]
\draw [color={rgb, 255:red, 0; green, 255; blue, 0 }  ,draw opacity=1 ]   (250,50) -- (348.59,148.59) ;
\draw [shift={(350,150)}, rotate = 225] [fill={rgb, 255:red, 0; green, 255; blue, 0 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (12,-3) -- (0,0) -- (12,3) -- cycle    ;
%Straight Lines [id:da24924523821630928]
\draw [color={rgb, 255:red, 255; green, 135; blue, 0 }  ,draw opacity=1 ]   (150,20) -- (247.88,117.88) ;
\draw [shift={(250,120)}, rotate = 225] [fill={rgb, 255:red, 255; green, 135; blue, 0 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (10.72,-5.15) -- (0,0) -- (10.72,5.15) -- (7.12,0) -- cycle    ;

\end{tikzpicture}
\end{document}
```

Converted output:

```tikz
% Color definitions
\definecolor{Blue}{rgb}{0.0000, 0.0000, 1.0000}
\definecolor{ElectricGreen}{rgb}{0.0000, 1.0000, 0.0000}
\definecolor{Red}{rgb}{1.0000, 0.0000, 0.0000}

% Setup
\usetikzlibrary{arrows.meta, decorations.markings, bending}
\tikzset{>={Stealth[length=6pt, width=4pt, bend]}}

\begin{document}

\begin{tikzpicture}[x = 0.75pt, y = 0.75pt, yscale = -1, line width = 0.75pt]
% Rendered in Obsidian mode

%Straight Lines [id:da42258022865066713]
\draw (120, 100) -- (220, 200);
%Straight Lines [id:da20377336023283854]
\draw[->, color = Red] (100, 150) -- (198.59, 248.59);
%Straight Lines [id:da6853171422293277]
\draw[->, color = Blue] (210, 130) -- (307.88, 227.88);
%Straight Lines [id:da6253093591230833]
\draw[->, color = ElectricGreen] (250, 50) -- (348.59, 148.59);
%Straight Lines [id:da08195472082160826]
\draw[>->, decoration = {markings, mark = at position 0.59 with {\arrow{>}}}, postaction = {decorate}] (150.71, 20.71) -- (208.59, 78.59);

\end{tikzpicture}

\end{document}
```

## Curves

Mathcha input:

```tikz

\tikzset{every picture/.style={line width=0.75pt}} %set default line width to 0.75pt        

\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1]
%uncomment if require: \path (0,300); %set diagram left start at 0, and has height of 300

%Curve Lines [id:da7425210995663132] 
\draw [color={rgb, 255:red, 232; green, 142; blue, 142 }  ,draw opacity=1 ] [dash pattern={on 4.5pt off 4.5pt}]  (90,70) .. controls (130,40) and (202,20.66) .. (180,60) .. controls (158,99.34) and (204,103.34) .. (200,130) .. controls (196,156.66) and (173,127.66) .. (150,150) .. controls (127,172.34) and (122,127.34) .. (70,150) .. controls (19.3,172.1) and (62.71,98.82) .. (88.09,71.97) ;
\draw [shift={(90,70)}, rotate = 135] [fill={rgb, 255:red, 232; green, 142; blue, 142 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle    ;
\draw [shift={(148,41.4)}, rotate = 163.12] [fill={rgb, 255:red, 232; green, 142; blue, 142 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle    ;
\draw [shift={(184.25,100.85)}, rotate = 229.56] [fill={rgb, 255:red, 232; green, 142; blue, 142 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle    ;
\draw [shift={(172.4,140.81)}, rotate = 3.4] [fill={rgb, 255:red, 232; green, 142; blue, 142 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle    ;
\draw [shift={(106.31,144.32)}, rotate = 15.57] [fill={rgb, 255:red, 232; green, 142; blue, 142 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle    ;
\draw [shift={(57.84,114.29)}, rotate = 118] [fill={rgb, 255:red, 232; green, 142; blue, 142 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle    ;
%Curve Lines [id:da6926512907629531] 
\draw [color={rgb, 255:red, 169; green, 219; blue, 255 }  ,draw opacity=1 ]   (232.45,190.07) .. controls (312.29,191.45) and (277.53,99.25) .. (330,190) .. controls (383,281.66) and (290,238.34) .. (230,190) ;
\draw [shift={(230,190)}, rotate = 2.3] [color={rgb, 255:red, 169; green, 219; blue, 255 }  ,draw opacity=1 ][line width=0.75]    (10.93,-3.29) .. controls (6.95,-1.4) and (3.31,-0.3) .. (0,0) .. controls (3.31,0.3) and (6.95,1.4) .. (10.93,3.29)   ;
%Curve Lines [id:da10517142515942057] 
\draw [color={rgb, 255:red, 255; green, 199; blue, 132 }  ,draw opacity=1 ]   (62.96,207.92) .. controls (100.63,183.19) and (120.6,238.13) .. (158.84,210.85) ;
\draw [shift={(160,210)}, rotate = 143.13] [color={rgb, 255:red, 255; green, 199; blue, 132 }  ,draw opacity=1 ][line width=0.75]    (10.93,-3.29) .. controls (6.95,-1.4) and (3.31,-0.3) .. (0,0) .. controls (3.31,0.3) and (6.95,1.4) .. (10.93,3.29)   ;
\draw [shift={(115.47,212.69)}, rotate = 206.17] [fill={rgb, 255:red, 255; green, 199; blue, 132 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle    ;
\draw [shift={(60,210)}, rotate = 323.13] [fill={rgb, 255:red, 255; green, 199; blue, 132 }  ,fill opacity=1 ][line width=0.08]  [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle    ;
%Curve Lines [id:da5811061872614517] 
\draw [color={rgb, 255:red, 118; green, 127; blue, 166 }  ,draw opacity=1 ]   (251.79,68.71) .. controls (290.6,41.78) and (310.6,99.55) .. (350,70) .. controls (390,40) and (375,105) .. (400,80) .. controls (425,55) and (425,115) .. (450,90) .. controls (474.63,65.37) and (474.99,123.22) .. (498.89,101.07) ;
\draw [shift={(500,100)}, rotate = 135] [color={rgb, 255:red, 118; green, 127; blue, 166 }  ,draw opacity=1 ][line width=0.75]    (10.93,-3.29) .. controls (6.95,-1.4) and (3.31,-0.3) .. (0,0) .. controls (3.31,0.3) and (6.95,1.4) .. (10.93,3.29)   ;
\draw [shift={(306.45,73.15)}, rotate = 205.94] [color={rgb, 255:red, 118; green, 127; blue, 166 }  ,draw opacity=1 ][line width=0.75]    (10.93,-4.9) .. controls (6.95,-2.3) and (3.31,-0.67) .. (0,0) .. controls (3.31,0.67) and (6.95,2.3) .. (10.93,4.9)   ;
\draw [shift={(381.14,74.25)}, rotate = 243.09] [color={rgb, 255:red, 118; green, 127; blue, 166 }  ,draw opacity=1 ][line width=0.75]    (10.93,-4.9) .. controls (6.95,-2.3) and (3.31,-0.67) .. (0,0) .. controls (3.31,0.67) and (6.95,2.3) .. (10.93,4.9)   ;
\draw [shift={(428.61,89.84)}, rotate = 233.26] [color={rgb, 255:red, 118; green, 127; blue, 166 }  ,draw opacity=1 ][line width=0.75]    (10.93,-4.9) .. controls (6.95,-2.3) and (3.31,-0.67) .. (0,0) .. controls (3.31,0.67) and (6.95,2.3) .. (10.93,4.9)   ;
\draw [shift={(478.26,99.41)}, rotate = 233.61] [color={rgb, 255:red, 118; green, 127; blue, 166 }  ,draw opacity=1 ][line width=0.75]    (10.93,-4.9) .. controls (6.95,-2.3) and (3.31,-0.67) .. (0,0) .. controls (3.31,0.67) and (6.95,2.3) .. (10.93,4.9)   ;
\draw [shift={(251.79,68.71)}, rotate = 143.13] [color={rgb, 255:red, 118; green, 127; blue, 166 }  ,draw opacity=1 ][line width=0.75]    (10.93,-4.9) .. controls (6.95,-2.3) and (3.31,-0.67) .. (0,0) .. controls (3.31,0.67) and (6.95,2.3) .. (10.93,4.9)   ;

\end{tikzpicture}
```

Converted output:

```tikz
% Color definitions
\definecolor{ColumbiaBlue}{rgb}{0.6078, 0.8667, 1.0000}
\definecolor{LightSlateGray}{rgb}{0.4667, 0.5333, 0.6000}
\definecolor{MacaroniAndCheese}{rgb}{1.0000, 0.7412, 0.5333}
\definecolor{RuddyPink}{rgb}{0.8824, 0.5569, 0.5882}

% Setup
\usetikzlibrary{arrows.meta, decorations.markings, bending}
\tikzset{>={Stealth[length=6pt, width=4pt, bend]}}

\begin{document}

\begin{tikzpicture}[x = 0.75pt, y = 0.75pt, yscale = -1, line width = 0.75pt]
% Rendered in Obsidian mode

%Curve Lines [id:da7425210995663132]
\draw[color = RuddyPink, >-, decoration = {markings, mark = at position 0.13 with {\arrow{>}},
mark = at position 0.35 with {\arrow{>}},
mark = at position 0.50 with {\arrow{>}},
mark = at position 0.66 with {\arrow{>}},
mark = at position 0.87 with {\arrow{>}}}, postaction = {decorate}, dashed] (90, 70) .. controls (130, 40) and (202, 20.66) .. (180, 60)
    .. controls (158, 99.34) and (204, 103.34) .. (200, 130)
    .. controls (196, 156.66) and (173, 127.66) .. (150, 150)
    .. controls (127, 172.34) and (122, 127.34) .. (70, 150)
    .. controls (19.3, 172.1) and (62.71, 98.82) .. (88.09, 71.97);
%Curve Lines [id:da6926512907629531]
\draw[color = ColumbiaBlue, <-] (232.45, 190.07) .. controls (312.29, 191.45) and (277.53, 99.25) .. (330, 190)
    .. controls (383, 281.66) and (290, 238.34) .. (230, 190);
%Curve Lines [id:da10517142515942057]
\draw[color = MacaroniAndCheese, <->, decoration = {markings, mark = at position 0.50 with {\arrow{>}}}, postaction = {decorate}] (62.96, 207.92) .. controls (100.63, 183.19) and (120.6, 238.13) .. (158.84, 210.85);
%Curve Lines [id:da5811061872614517]
\draw[color = LightSlateGray, >->, decoration = {markings, mark = at position 0.18 with {\arrow{>}},
mark = at position 0.47 with {\arrow{>}},
mark = at position 0.69 with {\arrow{>}},
mark = at position 0.90 with {\arrow{>}}}, postaction = {decorate}] (251.79, 68.71) .. controls (290.6, 41.78) and (310.6, 99.55) .. (350, 70)
    .. controls (390, 40) and (375, 105) .. (400, 80)
    .. controls (425, 55) and (425, 115) .. (450, 90)
    .. controls (474.63, 65.37) and (474.99, 123.22) .. (498.89, 101.07);

\end{tikzpicture}

\end{document}
```

## Ellipses, Circles, Arcs

Mathcha input:

```tikz

\tikzset{every picture/.style={line width=0.75pt}} %set default line width to 0.75pt

\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1]

%uncomment if require: \path (0,300); %set diagram left start at 0, and has height of 300

%Shape: Arc [id:dp8875726498241538]

\draw [draw opacity=0][dash pattern={on 4.5pt off 4.5pt}] (84.18,139.7) .. controls (78.67,146.21) and (72.08,150) .. (65,150) .. controls (45.67,150) and (30,121.79) .. (30,87) .. controls (30,52.21) and (45.67,24) .. (65,24) .. controls (84.33,24) and (100,52.21) .. (100,87) .. controls (100,87.29) and (100,87.57) .. (100,87.86) -- (65,87) -- cycle ; \draw [dash pattern={on 4.5pt off 4.5pt}] [dash pattern={on 4.5pt off 4.5pt}] (82.15,141.93) .. controls (77.08,147.07) and (71.23,150) .. (65,150) .. controls (45.67,150) and (30,121.79) .. (30,87) .. controls (30,52.21) and (45.67,24) .. (65,24) .. controls (84.33,24) and (100,52.21) .. (100,87) ; \draw [shift={(100,87.86)}, rotate = 267.42] [fill={rgb, 255:red, 0; green, 0; blue, 0 } ][dash pattern={on 3.49pt off 4.5pt}][line width=0.08] [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle ; \draw [shift={(84.18,139.7)}, rotate = 139.59] [fill={rgb, 255:red, 0; green, 0; blue, 0 } ][dash pattern={on 3.49pt off 4.5pt}][line width=0.08] [draw opacity=0] (8.93,-4.29) -- (0,0) -- (8.93,4.29) -- cycle ;

%Shape: Arc [id:dp8526636001263398]

\draw [draw opacity=0][dash pattern={on 4.5pt off 4.5pt}] (153.21,47.11) .. controls (151.7,41.93) and (151.88,37.98) .. (154.06,35.78) .. controls (161.83,27.92) and (192,45.16) .. (221.46,74.28) .. controls (250.92,103.4) and (268.5,133.37) .. (260.74,141.23) .. controls (252.97,149.09) and (222.8,131.85) .. (193.34,102.73) .. controls (175.4,84.99) and (161.86,66.94) .. (155.77,53.76) -- (207.4,88.5) -- cycle ; \draw [color={rgb, 255:red, 232; green, 142; blue, 142 } ,draw opacity=1 ][dash pattern={on 4.5pt off 4.5pt}] [dash pattern={on 4.5pt off 4.5pt}] (152.71,45.15) .. controls (151.78,40.93) and (152.16,37.69) .. (154.06,35.78) .. controls (161.83,27.92) and (192,45.16) .. (221.46,74.28) .. controls (250.92,103.4) and (268.5,133.37) .. (260.74,141.23) .. controls (252.97,149.09) and (222.8,131.85) .. (193.34,102.73) .. controls (175.4,84.99) and (161.86,66.94) .. (155.77,53.76) ; \draw [shift={(153.21,47.11)}, rotate = 270] [color={rgb, 255:red, 232; green, 142; blue, 142 } ,draw opacity=1 ][dash pattern={on 4.5pt off 4.5pt}][line width=0.75] (10.93,-3.29) .. controls (6.95,-1.4) and (3.31,-0.3) .. (0,0) .. controls (3.31,0.3) and (6.95,1.4) .. (10.93,3.29) ;

%Shape: Arc [id:dp1505515017757535]

\draw [draw opacity=0][dash pattern={on 0.84pt off 2.51pt}] (132.7,157.71) .. controls (130.96,155.34) and (130,152.73) .. (130,150) .. controls (130,138.95) and (145.67,130) .. (165,130) .. controls (167.44,130) and (169.83,130.14) .. (172.13,130.42) -- (165,150) -- cycle ; \draw [color={rgb, 255:red, 255; green, 199; blue, 132 } ,draw opacity=1 ][dash pattern={on 0.84pt off 2.51pt}] [dash pattern={on 0.84pt off 2.51pt}] (132.7,157.71) .. controls (130.96,155.34) and (130,152.73) .. (130,150) .. controls (130,138.95) and (145.67,130) .. (165,130) .. controls (166.75,130) and (168.46,130.07) .. (170.14,130.21) ; \draw [shift={(172.13,130.42)}, rotate = 181.07] [fill={rgb, 255:red, 255; green, 199; blue, 132 } ,fill opacity=1 ][dash pattern={on 0.08pt off 2.29pt}][line width=0.08] [draw opacity=0] (12,-3) -- (0,0) -- (12,3) -- cycle ;

%Shape: Arc [id:dp03855560983806183]

\draw [draw opacity=0] (171.99,176.66) .. controls (176.92,181.23) and (180,187.75) .. (180,195) .. controls (180,208.81) and (168.81,220) .. (155,220) .. controls (141.19,220) and (130,208.81) .. (130,195) .. controls (130,181.19) and (141.19,170) .. (155,170) .. controls (158,170) and (160.88,170.53) .. (163.55,171.5) -- (155,195) -- cycle ; \draw [color={rgb, 255:red, 174; green, 170; blue, 230 } ,draw opacity=1 ] (173.41,178.09) .. controls (177.5,182.54) and (180,188.48) .. (180,195) .. controls (180,208.81) and (168.81,220) .. (155,220) .. controls (141.19,220) and (130,208.81) .. (130,195) .. controls (130,181.19) and (141.19,170) .. (155,170) .. controls (156.97,170) and (158.88,170.23) .. (160.72,170.66) ; \draw [shift={(163.55,171.5)}, rotate = 186.36] [fill={rgb, 255:red, 174; green, 170; blue, 230 } ,fill opacity=1 ][line width=0.08] [draw opacity=0] (10.72,-5.15) -- (0,0) -- (10.72,5.15) -- (7.12,0) -- cycle ; \draw [shift={(171.99,176.66)}, rotate = 56.63] [color={rgb, 255:red, 174; green, 170; blue, 230 } ,draw opacity=1 ][line width=0.75] (10.93,-3.29) .. controls (6.95,-1.4) and (3.31,-0.3) .. (0,0) .. controls (3.31,0.3) and (6.95,1.4) .. (10.93,3.29) ;

\end{tikzpicture}
```

Converted output:

```tikz
% Color definitions
\definecolor{LightPastelPurple}{rgb}{0.6941, 0.6118, 0.8510}
\definecolor{MacaroniAndCheese}{rgb}{1.0000, 0.7412, 0.5333}
\definecolor{RuddyPink}{rgb}{0.8824, 0.5569, 0.5882}

% Setup
\usetikzlibrary{arrows.meta, decorations.markings, bending}
\tikzset{>={Stealth[length=6pt, width=4pt, bend]}}

\begin{document}

\begin{tikzpicture}[x = 0.75pt, y = 0.75pt, yscale = -1, line width = 0.75pt]
% Rendered in Obsidian mode

%Arc [id:dp8875726498241538]
\draw[<->, rotate around = {89.99 : (65, 87)}, dashed] ([shift = {(65, 87)}] -29.33 : 63 and 35) arc (-29.33 : 270 : 63 and 35);
%Arc [id:dp8526636001263398]
\draw[color = RuddyPink, <-, rotate around = {44.67 : (207.4, 88.5)}, dashed] ([shift = {(207.4, 88.5)}] 157.63 : 75.01 and 20) arc (157.63 : 504.6 : 75.01 and 20);
%Arc [id:dp1505515017757535]
\draw[color = MacaroniAndCheese, ->, dotted] ([shift = {(165.16, 150.06)}] 157.31 : 35.17 and 20.06) arc (157.31 : 278.05 : 35.17 and 20.06);
%Arc [id:dp03855560983806183]
\draw[color = LightPastelPurple, <->, rotate around = {19.77 : (155, 195)}] ([shift = {(155, 195)}] -62.34 : 25 and 25) arc (-62.34 : 263.45 : 25 and 25);

\end{tikzpicture}

\end{document}
```

