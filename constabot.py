import os
import random
import io
from dotenv import load_dotenv
import requests
import discord
import urllib.parse
import syllables
import base64
from playwright.async_api import async_playwright

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LEO_ID = os.getenv("LEO_ID")
WA_APP_ID = os.getenv("WA_APP_ID")
DESMOS_API_KEY = os.getenv("DESMOS_API_KEY")

client = discord.Client(intents=discord.Intents.all())

DESMOS_HTML = f"""<!DOCTYPE html>
<html><head>
<script src="https://www.desmos.com/api/v1.9/calculator.js?apiKey={DESMOS_API_KEY}"></script>
</head>
<body style="margin:0">
<div id="calc" style="width:900px;height:600px"></div>
</body></html>"""
SCREENSHOT_JS = """
(exprs) => new Promise((resolve) => {
    const calc = Desmos.GraphingCalculator(
        document.getElementById('calc')
    );
    exprs.forEach((latex, i) => calc.setExpression({ id: 'e' + i, latex: latex }));
    calc.asyncScreenshot(
        { width: 900, height: 600, targetPixelRatio: 2 },
        (dataUri) => resolve(dataUri)
    );
})"""

async def graph_command(message):
    graph_expressions = [
        e.strip() for e in message.content.lower().replace("!graph", "").split(";") if e.strip()
    ]
    if not graph_expressions:
        await message.channel.send("Please provide a mathematical expression to graph after `!graph`")
        return

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 900, "height": 600})
            await page.set_content(DESMOS_HTML, wait_until="load")
            data_uri = await page.evaluate(SCREENSHOT_JS, graph_expressions)
            await browser.close()

        png_bytes = base64.b64decode(data_uri.split(",", 1)[1])
        await message.channel.send(file=discord.File(io.BytesIO(png_bytes), filename="graph.png"))
    except Exception as e:
        print(e)
        await message.channel.send(f"Error: {e}")    

async def wa_command(message):
    wa_query = message.content.lower().replace("!wa", "").strip()
    if wa_query:
        try:
            query = urllib.parse.quote_plus(wa_query)
            query_url = f"http://api.wolframalpha.com/v2/query?" \
            f"appid={WA_APP_ID}" \
            f"&input={query}" \
            f"&format=plaintext" \
            f"&output=json"

            r = requests.get(query_url).json()
            data = r["queryresult"]["pods"][1]["subpods"][0]
            if "datasources" in data:
                datasource = ", ".join(data["datasources"])
            else:
                datasource = "N/A"
            if "microsources" in data:
                microsource = ", ".join(data["microsources"])
            else:
                microsource = "N/A"
            plaintext = data["plaintext"]
            await message.channel.send(f"Result:\n{plaintext}\n\nDatasources: {datasource}\nMicrosources: {microsource}")
        except Exception as e:
            print(e)
            await message.channel.send(f"Error: {e}")
    else:
        await message.channel.send("Please provide a Wolfram|Alpha query after `!wa`")

async def mg_command(message):
    mg_query = message.content.lower().replace("!mg", "").strip()
    if mg_query:
        shop_data = requests.get("https://magicgarden.gg/platform/v1/shops").json()
        try:
            if mg_query == "weather":
                if shop_data["weather"]["current"] is None:
                    await message.channel.send("Weather: None")
                else:
                    weather_data = shop_data["weather"]["current"]["name"]
                    await message.channel.send(f"Weather: {weather_data}")

            elif mg_query == "seed":
                seed_data = shop_data["shops"]["seed"]["items"]
                seed_names = [item["name"] for item in seed_data]
                seed_stock = [item["stock"] for item in seed_data]
                seed_prices = [item["coinPrice"] for item in seed_data]
                await message.channel.send(f"Seed Shop:\n" + "\n".join([f"{name}: {stock} ({price} coins)" for name, stock, price in zip(seed_names, seed_stock, seed_prices)]))

            elif mg_query == "egg":
                egg_data = shop_data["shops"]["egg"]["items"]
                egg_names = [item["name"] for item in egg_data]
                egg_stock = [item["stock"] for item in egg_data]
                egg_prices = [item["coinPrice"] for item in egg_data]
                await message.channel.send(f"Egg Shop:\n" + "\n".join([f"{name}: {stock} ({price} coins)" for name, stock, price in zip(egg_names, egg_stock, egg_prices)]))

            elif mg_query == "tool":
                tool_data = shop_data["shops"]["tool"]["items"]
                tool_names = [item["name"] for item in tool_data]
                tool_stock = [item["stock"] for item in tool_data]
                tool_prices = [item["coinPrice"] for item in tool_data]
                await message.channel.send(f"Tool Shop:\n" + "\n".join([f"{name}: {stock} ({price} coins)" for name, stock, price in zip(tool_names, tool_stock, tool_prices)]))

            elif mg_query == "decor":
                decor_data = shop_data["shops"]["decor"]["items"]
                decor_names = [item["name"] for item in decor_data]
                decor_stock = [item["stock"] for item in decor_data]
                decor_prices = [item["coinPrice"] for item in decor_data]
                await message.channel.send(f"Decor Shop:\n" + "\n".join([f"{name}: {stock} ({price} coins)" for name, stock, price in zip(decor_names, decor_stock, decor_prices)]))

            else:
                await message.channel.send("Invalid Magic Garden query. Please use `!mg weather`, `!mg seed`, `!mg egg`, `!mg tool`, or `!mg decor`.")

        except Exception as e:
            print(e)
            await message.channel.send(f"Error: {e}")

    else:
        await message.channel.send("Please provide a Magic Garden query after `!mg`")

async def choose_command(message):
    try:
        options = message.content.lower().replace("!choose", "").strip().split(",")
        if len(options) < 2:
            raise ValueError("Not enough options provided")
        else:
            choice = random.choice([option.strip() for option in options])
            await message.channel.send(f"I choose: {choice}")
    except Exception as e:
        print(e)
        await message.channel.send(f"Error: {e}. Please use the format `!choose option1, option2, ...`.")

async def roll_command(message):
    try:
        (num, faces) = map(int, message.content.lower().replace("!roll", "").strip().split("d"))
        if num < 1 or faces < 1:
            raise ValueError("Number of dice and faces must be positive integers")
        rolls = [random.randint(1, faces) for _ in range(num)]
        await message.channel.send(f"Rolls: {rolls}\nTotal: {sum(rolls)}")
    except Exception as e:
        print(e)
        await message.channel.send(f"Error: {e}. Please use the format `!roll NdM` where N is the number of dice and M is the number of faces.")

async def help_command(message):
    help_message = (
        "Available commands:\
        `!graph <expression>` - Graphs the given mathematical expression.\
        `!wa <query>` - Queries Wolfram|Alpha for the given input.\
        `!choose option1, option2, ...` - Randomly chooses one of the provided options.\
        `!roll NdM` - Rolls N dice with M faces and returns the results.\
        `!mg <query>` - Queries the Magic Garden API for information. Valid queries are `weather`, `seed`, `egg`, `tool`, and `decor`.\
        `!help` - Displays this help message."
    )
    await message.channel.send(help_message)

async def haiku(message):
    split = message.content.lower().split()
    for i in range(len(split) - 2):
        first = split[:(i + 1)]
        if syllables.estimate(" ".join(first)) == 5:
            for j in range(i + 1, len(split) - 1):
                second = split[(i + 1):(j + 1)]
                if syllables.estimate(" ".join(second)) == 7:
                    third = split[(j + 1):]
                    if syllables.estimate(" ".join(third)) == 5:
                        haiku_text = " ".join(first) + "\n" + " ".join(second) + "\n" + " ".join(third)
                        await message.channel.send(f"Haiku detected:\n{haiku_text}")
                        return

command_prefixes = {
    "!graph": graph_command,
    "!wa": wa_command,
    "!mg": mg_command,
    "!choose": choose_command,
    "!roll": roll_command,
    "!help": help_command
}

math_responses = {
    "shiv": f"@{os.getenv("SHIV_ID")}",
    "game": "You just lost the game",
    "rogers": "It was a rather cold day at State High. The winds were roaring as a thunderstorm beat down on the school. Mr. Rogers hated the rain. It constantly reminded of his life before he met him.\nBOOM! Lightning struck, a blinding white flash causing everyone in the classroom to involuntarily close their eyes for a moment. Everyone except Mr. Constable.\n\"Mr. Constable, how is it that you never fear thunder?\" Mr. Rogers asked, peeking out from under his desk.\n\"Why do I not fear thunder? Because of a dream I had many years ago.\"\n\"A dream?\"\"Yes. A dream. A beautiful dream where, on a dark and stormy day much like this, I met the one that could be my equal. Since that day, I have worked quickly and confidently to find the one who could replace me.\"\nMr. Constable seemed to deflate a little, his expression souring as he recalled the years of waiting in vain.\n\"Alas, I have yet to find them,\" Mr. Constable plainly stated.\nMr. Rogers felt a pain in his chest, perhaps inspired by the dedication Mr. Constable had, but also perhaps because he understood the pain that came with searching for something that would never come. In that moment, Mr. Rogers was no longer afraid of the thunder.\n\"No, Mr. Cons-Tyler. You have me.\"",
    "math": "Mathematics is a field of knowledge concerned with abstract concepts such as numbers, geometric shapes, sets, functions, and probabilities.",
    "desmos": "Desmos is an advanced graphing calculator implemented as a web application and a mobile application written in TypeScript and JavaScript.",
    "rational function": "In mathematics, a rational function is any function that can be defined by a rational fraction, which is an algebraic fraction such that both the numerator and the denominator are polynomials. The coefficients of the polynomials need not be rational numbers; they may be taken in any field K. In this case, one speaks of a rational function and a rational fraction over K. The values of the variables may be taken in any field L containing K. Then the domain of the function is the set of the values of the variables for which the denominator is not zero, and the codomain is L.",
    "function": "In mathematics, a function from a set X to a set Y assigns to each element of X exactly one element of Y. The set X is called the domain of the function and the set Y is called the codomain of the function.",
    "polynomial": "In mathematics, a polynomial is a mathematical expression consisting of indeterminates (also called variables) and coefficients, that involves only the operations of addition, subtraction, multiplication and exponentiation to nonnegative integer powers, and has a finite number of terms. An example of a polynomial of a single indeterminate x is x^2 - 4x + 7. An example with three indeterminates is x^3 + 2xyz^2 - yz + 1.",
    "exponential": "In mathematics, the exponential function is the unique real function which maps zero to one and has a derivative everywhere equal to its value. It is denoted e^x or exp x; the latter is preferred when the argument x is a complicated expression. It is called exponential because its argument can be seen as an exponent to which a constant number e ≈ 2.718, the base, is raised. There are several other definitions of the exponential function, which are all equivalent although being of very different nature.",
    "logarithm": "In mathematics, the logarithm of a number is the exponent by which another fixed value, the base, must be raised to produce that number. For example, the logarithm of 1000 to base 10 is 3, because 1000 is 10 to the 3rd power: 1000 = 103 = 10 × 10 × 10. More generally, if x = by, then y is the logarithm of x to base b, written logb x = y, so log10 1000 = 3. As a single-variable function, the logarithm to base b is the inverse of exponentiation with base b.",
    "sequence": "In mathematics, a sequence is a collection of objects possibly with repetition, that come in a specified order. Like a set, it contains members (also called elements, or terms). Unlike a set, the same elements can appear multiple times at different positions in a sequence, and unlike a set, the order does matter. The notion of a sequence can be generalized to an indexed family, defined as a function from an arbitrary index set.",
    "series": "In mathematics, a series is, roughly speaking, an addition of infinitely many terms, one after the other. The study of series is a major part of calculus and its generalization, mathematical analysis. Series are used in most areas of mathematics, even for studying finite structures in combinatorics through generating functions. The mathematical properties of infinite series make them widely applicable in other quantitative disciplines such as physics, computer science, statistics and finance.",
    "probability": "Probability concerns events and numerical descriptions of how likely they are to occur. The probability of an event is a number between 0 and 1; the larger the probability, the more likely an event is to occur. This number is often expressed as a percentage (%), ranging from 0% to 100%. A simple example is the tossing of a fair (unbiased) coin. Since the coin is fair, the two outcomes (\"heads\" and \"tails\") are both equally probable; the probability of \"heads\" is the same asthe probability of \"tails\". Since no other outcomes are possible,the probability of either \"heads\" or \"tails\" is 1/2 (which could also be written as 0.5 or 50%).",
    "inverse trig": "In mathematics, inverse trigonometric functions are the inverse functions of the trigonometric functions with suitably restricted domains.",
    "inverse": "In mathematics, the inverse function of a function f (also called the inverse of f) is a function that undoes the operation of f. The inverse of f exists if and only if f is bijective, and if it exists, is denoted by f^-1.",
    "rational": "In mathematics, a rational number is a number that can be expressed as the quotient or fraction p/q of two integers, a numerator p and a nonzero denominator q. For example, 3/7 is a rational number, as is every integer (for example, -5 = -5/1). The set of all rational numbers is often referred to as \"the rationals\", and is closed under addition, subtraction, multiplication, and division by a nonzero rational number. It is a field under these operations and therefore also called the field of rationals or the field of rational numbers. It is usually denoted by boldface Q, or blackboard bold ℚ.",
    "fraction": "A fraction (from Latin: fractus, \"broken\") represents a part of a whole or, more generally, any number of equal parts. When spoken in everyday English, a fraction describes how many parts of a certain size there are, for example, one-half, eight-fifths, three-quarters. A simple fraction (examples: 1/2 and 17/3) consists of an integer numerator, displayed above a line (or before a slash like 1/2), and a non-zero integer denominator, displayed below (or after) that line. If these integers are positive, then the numerator represents a number of equal parts, and the denominator indicates how many of those parts make up a unit or a whole. For example, in the fraction 3/4, the numerator 3 indicates that the fraction represents 3 equal parts, and the denominator 4 indicates that 4 parts make up a whole. The picture to the right illustrates 3/4 of a cake.",
    "graph": "In mathematics, the graph of a function f is the set of ordered pairs (x,y), where f(x) = y. In the common case where x and f(x) are real numbers, these pairs are Cartesian coordinates of points in a plane and often form a curve. The graphical representation of the graph of a function is also known as a plot.",
    "trig": "In mathematics, trigonometry (from Ancient Greek τρίγωνον (trígōnon) 'triangle' and μέτρον (métron) 'measure') is a branch of mathematics concerned with relationships between angles and side lengths of triangles. In particular, the trigonometric functions relate the angles of a right triangle with ratios of its side lengths.",
    "sin": "In mathematics, sine and cosine are trigonometric functions of an angle. The sine and cosine of an acute angle are defined in the context of a right triangle: for the specified angle, its sine is the ratio of the length of the side opposite that angle to the length of the longest side of the triangle (the hypotenuse), and the cosine is the ratio of the length of the adjacent leg to that of the hypotenuse. For an angle θ, the sine and cosine functions are denoted as sin(θ) and cos(θ).",
    "cos": "In mathematics, sine and cosine are trigonometric functions of an angle. The sine and cosine of an acute angle are defined in the context of a right triangle: for the specified angle, its sine is the ratio of the length of the side opposite that angle to the length of the longest side of the triangle (the hypotenuse), and the cosine is the ratio of the length of the adjacent leg to that of the hypotenuse. For an angle θ, the sine and cosine functions are denoted as sin(θ) and cos(θ).",
    "complex": "In mathematics, a complex number is an element of a number system that extends the real numbers with a specific element denoted i, called the imaginary unit and satisfying the equation i^2 = -1. Since no real number satisfies the above equation, i was called an imaginary number by René Descartes. Every complex number can be expressed in the form a+bi, where a and b are real numbers, a is called the real part, and b is called the imaginary part. The set of complex numbers is denoted by either of the symbols ℂ or C. Despite the historical nomenclature, \"imaginary\" numbers are not fictitious: they are no less real mathematically than real numbers, and they are essential to the scientific description of the physical world.",
    "imaginary": "An imaginary number is the product of a real number and the imaginary unit i, which is defined by its property i^2 =-1. The square of an imaginary number bi is -b^2. For example, 5i is an imaginary number, and its square is -25. The number zero is considered to be both real and imaginary.",
    "polar": "In mathematics, the polar coordinate system specifies a given point in a plane by using a distance and an angle as its two coordinates. These are the point's distance from a reference point called the pole, and the point's direction from the pole relative to the direction of the polar axis, a ray drawn from the pole. The distance from the pole is called the radial coordinate, radial distance or simply radius, and the angle is called the angular coordinate, polar angle, or azimuth. The pole is analogous to the origin in a Cartesian coordinate system.",
    "parametric": "In mathematics, a parametric equation expresses several quantities, such as the coordinates of a point, as functions of one or more variables called parameters. In the case of a single parameter, parametric equations are commonly used to express the trajectory of a moving point. For this case, the parameter is often, but not necessarily, time, and the point describes a curve, called a parametric curve. In the case of two parameters, the point describes a surface, called a parametric surface. In all cases, the equations are collectively called a parametric representation, or parametric system, or parameterization (also spelled parametrization, parametrisation) of the object.",
    "vector": "In mathematics and physics, a vector is an element of a vector space. A vector space is a collection of objects called vectors, which may be added together and multiplied by numbers, called scalars in this context. Scalars are often taken to be real numbers, but there are also vector spaces with scalar multiplication by complex numbers, rational numbers, or generally any field. The operations of vector addition and scalar multiplication must satisfy certain requirements, called axioms, listed below. The concept of a vector space is fundamental in linear algebra and related fields of mathematics.",
    "conic": "In mathematics, a conic section (or simply conic) is a curve obtained as the intersection of the surface of a cone with a plane. The three types of conic section are the hyperbola, the parabola, and the ellipse; the circle is a special case of the ellipse, though it was sometimes considered a fourth type. The ancient Greek mathematicians studied conic sections, culminating around 200 BC with Apollonius of Perga's systematic work on their properties.",
    "spreadsheet": "A spreadsheet is a computer application for computation, organization, analysis and storage of data in tabular form. Spreadsheets were developed as computerized analogs of paper accounting worksheets. The program operates on data entered in cells of a table. Each cell may contain either numeric or text data, or the results of formulas that automatically calculate and display a value based on the contents of other cells. The term spreadsheet may also refer to one such electronic document.",
    "limit": "In mathematics, a limit is the value that a function (or sequence) approaches as the argument (or index) approaches some value. Limits of functions are essential to calculus and mathematical analysis, and are used to define continuity, derivatives, and integrals. The concept of a limit of a sequence is further generalized to the concept of a limit of a topological net, and is closely related to limit and direct limit in category theory. The limit inferior and limit superior provide generalizations of the concept of a limit which are particularly relevant when the limit at a point may not exist.",
    "secant": "In geometry, a secant is a line that intersects a curve at a minimum of two distinct points. The word secant comes from the Latin word secare, meaning \"to cut\". In the case of a circle, a secant intersects the circle at exactly two points. A chord is the line segment determined by the two points, that is, the interval on the secant whose ends are the two points.",
    "tangent": "In geometry, the tangent line (or simply tangent) to a plane curve at a given point is, intuitively, the straight line that \"just touches\" the curve at that point. Leibniz defined it as the line through a pair of infinitely close points on the curve. More precisely, a straight line is tangent to the curve y = f(x) at a point x=c if the line passes through the point (c,f(c)) on the curve and has slope f'(c), where f' is the derivative of f. A similar definition applies to space curves and curves in n-dimensional Euclidean space.",
    "derivative": "In mathematics, the derivative is a fundamental tool that quantifies the sensitivity to change of a function's output with respect to its input. The derivative of a function of a single variable at a chosen input value, when it exists, is the slope of the tangent line to the graph of the function at that point. The tangent line is the best linear approximation of the function near that input value. The derivative is often described as the instantaneous rate of change, the ratio of the instantaneous change in the dependent variable to that of the independent variable. The process of finding a derivative is called differentiation.",
    "integral": "In mathematics, an integral is the continuous analog of a sum, and is used to calculate areas, volumes, and their generalizations. The process of computing an integral, called integration, is one of the two fundamental operations of calculus, along with differentiation. Integration was initially used to solve problems in mathematics and physics, such as finding the area under a curve, or determining displacement from velocity. Usage of integration expanded to a wide variety of scientific fields thereafter.",
    "real": "In mathematics, a real number is a number that can be used to measure a continuous one-dimensional quantity such as a length, duration or temperature. Here, continuous means that pairs of values can have arbitrarily small differences. Every real number can be almost uniquely represented by an infinite decimal expansion.",
    "natural": "In mathematics, the natural numbers are the numbers 0, 1, 2, 3, and so on, possibly excluding 0. The terms positive integers, non-negative integers, whole numbers, and counting numbers are also used. The set of the natural numbers is commonly denoted by a bold N or a blackboard bold ℕ.",
    "integer": "An integer is the number zero (0), a positive natural number (1, 2, 3, ...), or the negation of a positive natural number (-1, -2, -3, ...). The negations or additive inverses of the positive natural numbers are referred to as negative integers. The set of all integers is often denoted by the boldface Z or blackboard bold ℤ.",
    "number": "A number is a mathematical object used to count, measure, and label. The most basic examples are the natural numbers: 1, 2, 3, 4, 5, and so forth. Individual numbers can be represented in spoken or written language with number words, or with dedicated symbols called numerals; for example, \"eleven\" is a number word and \"11\" is the corresponding numeral. As only a limited list of symbols can be memorized, a numeral system is used to represent any number in an organized way. The most common representation is the Hindu-Arabic numeral system, a decimal system which can display any non-negative integer using a combination of ten Arabic numeral symbols called digits. Numerals can be used for counting (as with cardinal number of a collection or set), for labelling (as with telephone numbers), for ordering (as with serial numbers), and for codes (as with ISBNs). In common usage, however, a numeral is not clearly distinguished from the number that it represents.",
    "calculus": "Calculus is the branch of mathematics that studies continuous change, and is the principal precursor of modern mathematical analysis. Originally called infinitesimal calculus or the calculus of infinitesimals, it has two major branches, differential calculus and integral calculus. Differential calculus studies instantaneous rates of change and slopes of curves; integral calculus studies accumulation of quantities and areas under or between curves. These two branches are related to each other by the fundamental theorem of calculus. Calculus uses convergence of infinite sequences and infinite series to a well-defined mathematical limit.",
    "linear algebra": "Linear algebra is the branch of mathematics concerning linear equations such as a1x1 + ⋯ + anxn = b, linear maps such as the following: (x1,…,xn) ↦ a1x1 + ⋯ + anxn, and their representations in vector spaces and through matrices. In three-dimensional Euclidean space, these three planes represent solutions to linear equations, and their intersection represents the set of common solutions: in this case, a unique point. The blue line is the common solution to two of these equations. Linear algebra is central to almost all areas of mathematics. For instance, linear algebra is fundamental in modern presentations of geometry, including for defining basic objects such as lines, planes and rotations. Also, functional analysis, a branch of mathematical analysis, may be viewed as the application of linear algebra to function spaces.",
    "algebra": "Algebra is a branch of mathematics that deals with abstract systems, known as algebraic structures, and the manipulation of expressions within those systems. It is a generalization of arithmetic that introduces variables and algebraic operations other than the standard arithmetic operations, such as addition and multiplication.",
    "matrix": "In mathematics, a matrix (pl.: matrices) is a rectangular array of numbers or other mathematical objects with elements or entries arranged in rows and columns, usually satisfying certain properties of addition and multiplication.",
    "calculator": "A calculator is typically a portable electronic device used to perform calculations, ranging from basic arithmetic to complex mathematics.",
    "calc": "Short for calculator btw",
    "stat": "Statistics (from German: Statistik, orig. \"description of a state, a country\") is the discipline that concerns the collection, organization, analysis, interpretation, and presentation of data. In applying statistics to a scientific, industrial, or social problem, it is conventional to begin with a statistical population or a statistical model to be studied. Populations can be diverse groups of people or objects such as \"all people living in a country\" or \"every atom composing a crystal\". Statistics deals with every aspect of data, including the planning of data collection in terms of the design of surveys and experiments. Statistics is deeply related to subjects like physics, chemistry, geography, geopolitics, and especially mathematics.",
    "euler": "Leonhard Euler (/ˈɔɪlər/ OY-lər; 15 April 1707 - 18 September 1783) was a Swiss polymath who was active as a mathematician, physicist, astronomer, logician, geographer, music theorist and engineer. He founded the studies of graph theory and topology and made influential discoveries in many other branches of mathematics, such as analytic number theory, complex analysis, and infinitesimal calculus. He also introduced much of modern mathematical terminology and notation, including the notion of a mathematical function. He is known for his work in mechanics, fluid dynamics, optics, astronomy, and music theory. Euler has been called a \"universal genius\" who \"was fully equipped with almost unlimited powers of imagination, intellectual gifts and extraordinary memory\". He spent most of his adult life in Saint Petersburg, Russia, and in Berlin, then the capital of Prussia.",
    "gauss": "Johann Carl Friedrich Gauss (/ɡaʊs/; German: Gauß; 30 April 1777 - 23 February 1855) was a German mathematician, astronomer, geodesist, and physicist, who contributed to many fields in mathematics and science. His mathematical contributions spanned the branches of number theory, algebra, analysis, geometry, statistics, and probability. Gauss was director of the Göttingen Observatory in Germany and professor of astronomy from 1807 until his death in 1855.",
    "pythagoras": "Pythagoras of Samos (Ancient Greek: Πυθαγόρας; c. 570 - c. 495 BC) was an ancient Ionian Greek philosopher, polymath, and the eponymous founder of Pythagoreanism. His political and religious teachings were well known in Magna Graecia and influenced the philosophies of Plato, Aristotle, and, through them, Western philosophy. Modern scholars disagree regarding Pythagoras's education and influences, but most agree that he travelled to Croton in southern Italy around 530 BC, where he founded a school in which initiates were allegedly sworn to secrecy and lived a communal, ascetic lifestyle.",
    "pythagorean": "In mathematics, the Pythagorean theorem or Pythagoras's theorem is a fundamental relation in Euclidean geometry between the three sides of a right triangle. It states that the area of the square whose side is the hypotenuse (the side opposite the right angle) is equal to the sum of the areas of the squares on the other two sides.",
    "euclid": "Euclid (Ancient Greek: Εὐκλείδης; c. 300 BC) was a Greek mathematician, often referred to as the \"father of geometry\". He was active in Alexandria during the reign of Ptolemy I (c. 323 - 283 BC). His Elements is one of the most influential works in the history of mathematics, serving as the main textbook for teaching geometry from the time of Euclid until the late 19th century.",
    "newton": "Sir Isaac Newton (4 January 1643 - 31 March 1727) was an English mathematician, physicist, astronomer, alchemist, theologian, and author who is widely recognised as one of the most influential scientists of all time and a key figure in the scientific revolution. His book Philosophiæ Naturalis Principia Mathematica (Mathematical Principles of Natural Philosophy), first published in 1687, laid the foundations of classical mechanics. Newton also made seminal contributions to optics and shares credit with German mathematician Gottfried Wilhelm Leibniz for developing infinitesimal calculus.",
    "archimedes": "Archimedes of Syracuse (c. 287 - c. 212 BC) was an ancient Greek mathematician, physicist, engineer, inventor, and astronomer. He is regarded as one of the leading scientists in classical antiquity and one of the greatest mathematicians of all time. Archimedes anticipated modern calculus and analysis by applying the concept of infinitesimals and the method of exhaustion to derive and rigorously prove many geometrical theorems.",
    "leibniz": "Gottfried Wilhelm Leibniz (1 July 1646 - 14 November 1716) was a German polymath and philosopher who is credited with developing calculus independently of Isaac Newton. He made significant contributions to philosophy, logic, mathematics, physics, and technology, and is considered one of the last universal geniuses.",
    "riemann": "Georg Friedrich Bernhard Riemann (17 September 1826 - 20 July 1866) was a German mathematician who made profound contributions to analysis, number theory, and differential geometry. He is best known for the Riemann hypothesis, a conjecture about the distribution of prime numbers.",
    "pi": "The number π (pi) is a mathematical constant that represents the ratio of a circle's circumference to its diameter. It is approximately equal to 3.14159 and is an irrational number, meaning it cannot be expressed as a simple fraction.",
    "e": "The number e is a mathematical constant approximately equal to 2.71828, which is the base of the natural logarithm. It is an irrational number and has important applications in calculus, complex analysis, and number theory."
}

reaction_triggers = {
    "leo": "leo1",
    "scott": "scottie",
    "tsa": "tsa",
    "ella": "ellamog",
    "graham": "grahamknife",
    "gilbert": "gilbow",
    "maggie": "maggie"
}

async def react(message, trigger):
    emoji_name = reaction_triggers.get(trigger)
    if emoji_name:
        emoji = discord.utils.get(client.emojis, name=emoji_name)
        if emoji:
            await message.add_reaction(emoji)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')    

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower()

    if syllables.estimate(content) == 17:
        await haiku(message)

    if message.author.id == LEO_ID:
        await react(message, "leo")

    for prefix, command in command_prefixes.items():
        if content.startswith(prefix):
            await command(message)
            return
    
    for trigger in reaction_triggers.keys():
        if trigger in content.split():
            await react(message, trigger)
            content = content.replace(trigger, "")

    for keyword, response in math_responses.items():
        if keyword in content.split():
            await message.channel.send(response)
            content = content.replace(keyword, "")

    if "consty" in content.split() or "constable" in content.split() or "constabot" in content.split():
        await message.channel.send(file=discord.File('absolute_honors.png'))
        content = content.replace("consty", "").replace("constable", "").replace("constabot", "")

    if "benny" in content.split() or "benjamin" in content.split() or "gulis" in content.split():
        await message.channel.send(file=discord.File('gulis_impressed.png'))
        content = content.replace("benny", "").replace("benjamin", "").replace("gulis", "")

client.run(DISCORD_TOKEN)