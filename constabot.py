import os
from dotenv import load_dotenv
import discord
#import quote

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LEO_ID = os.getenv("LEO_ID")

client = discord.Client(intents=discord.Intents.all())

custom_leo = discord.utils.get(client.emojis, name='leo1')
custom_scott = discord.utils.get(client.emojis, name='scottie')
custom_tsa = discord.utils.get(client.emojis, name='tsa')

math_dict = {
    "math": "Mathematics is a field of knowledge concerned with abstract concepts such as numbers, geometric shapes, sets, functions, and probabilities. It uses logical reasoning and proof to study and establish their properties, often expressed as theorems, formulas, and equations. Mathematics is used to model and solve problems in science, engineering, technology, economics, and everyday life.",
    "desmos": "Desmos is an advanced graphing calculator implemented as a web application and a mobile application written in TypeScript and JavaScript.",
    "function": "In mathematics, a function from a set X to a set Y assigns to each element of X exactly one element of Y. The set X is called the domain of the function and the set Y is called the codomain of the function.",
    "graph": "In mathematics, the graph of a function f is the set of ordered pairs (x,y), where f(x)=y. In the common case where x and f(x) are real numbers, these pairs are Cartesian coordinates of points in a plane and often form a curve. The graphical representation of the graph of a function is also known as a plot.",
    "polynomial": "In mathematics, a polynomial is a mathematical expression consisting of indeterminates (also called variables) and coefficients, that involves only the operations of addition, subtraction, multiplication and exponentiation to nonnegative integer powers, and has a finite number of terms. An example of a polynomial of a single indeterminate x is x^2-4x+7. An example with three indeterminates is x^3+2xyz^2-yz+1.",
    "rational function": "In mathematics, a rational function is any function that can be defined by a rational fraction, which is an algebraic fraction such that both the numerator and the denominator are polynomials. The coefficients of the polynomials need not be rational numbers; they may be taken in any field K. In this case, one speaks of a rational function and a rational fraction over K. The values of the variables may be taken in any field L containing K. Then the domain of the function is the set of the values of the variables for which the denominator is not zero, and the codomain is L.",
    "exponential": "In mathematics, the exponential function is the unique real function which maps zero to one and has a derivative everywhere equal to its value. It is denoted e^x or exp x; the latter is preferred when the argument x is a complicated expression. It is called exponential because its argument can be seen as an exponent to which a constant number e ≈ 2.718, the base, is raised. There are several other definitions of the exponential function, which are all equivalent although being of very different nature.",
    "logarithm": "In mathematics, the logarithm of a number is the exponent by which another fixed value, the base, must be raised to produce that number. For example, the logarithm of 1000 to base 10 is 3, because 1000 is 10 to the 3rd power: 1000 = 103 = 10 × 10 × 10. More generally, if x = by, then y is the logarithm of x to base b, written logb x = y, so log10 1000 = 3. As a single-variable function, the logarithm to base b is the inverse of exponentiation with base b.",
    "sequence": "In mathematics, a sequence is a collection of objects possibly with repetition, that come in a specified order. Like a set, it contains members (also called elements, or terms). Unlike a set, the same elements can appear multiple times at different positions in a sequence, and unlike a set, the order does matter. The notion of a sequence can be generalized to an indexed family, defined as a function from an arbitrary index set.",
    "series": "In mathematics, a series is, roughly speaking, an addition of infinitely many terms, one after the other. The study of series is a major part of calculus and its generalization, mathematical analysis. Series are used in most areas of mathematics, even for studying finite structures in combinatorics through generating functions. The mathematical properties of infinite series make them widely applicable in other quantitative disciplines such as physics, computer science, statistics and finance.",
    "probability": "Probability concerns events and numerical descriptions of how likely they are to occur. The probability of an event is a number between 0 and 1; the larger the probability, the more likely an event is to occur. This number is often expressed as a percentage (%), ranging from 0% to 100%. A simple example is the tossing of a fair (unbiased) coin. Since the coin is fair, the two outcomes (\"heads\" and \"tails\") are both equally probable; the probability of \"heads\" is the same asthe probability of \"tails\". Since no other outcomes are possible,the probability of either \"heads\" or \"tails\" is 1/2 (which could also be written as 0.5 or 50%).",
    "trig": "Trigonometry (from Ancient Greek τρίγωνον (trígōnon) 'triangle' and μέτρον (métron) 'measure') is a branch of mathematics concerned with relationships between angles and side lengths of triangles. In particular, the trigonometric functions relate the angles of a right triangle with ratios of its side lengths. The field emerged in the Hellenistic world during the 3rd century BC from applications of geometry to astronomical studies. The Greeks focused on the calculation of chords, while mathematicians in India created the earliest-known tables of values for trigonometric ratios (also called trigonometric functions) such as sine.",
    "sin": "In mathematics, sine and cosine are trigonometric functions of an angle. The sine and cosine of an acute angle are defined in the context of a right triangle: for the specified angle, its sine is the ratio of the length of the side opposite that angle to the length of the longest side of the triangle (the hypotenuse), and the cosine is the ratio of the length of the adjacent leg to that of the hypotenuse. For an angle θ, the sine and cosine functions are denoted as sin(θ) and cos(θ).",
    "cos": "In mathematics, sine and cosine are trigonometric functions of an angle. The sine and cosine of an acute angle are defined in the context of a right triangle: for the specified angle, its sine is the ratio of the length of the side opposite that angle to the length of the longest side of the triangle (the hypotenuse), and the cosine is the ratio of the length of the adjacent leg to that of the hypotenuse. For an angle θ, the sine and cosine functions are denoted as sin(θ) and cos(θ).",
    "inverse trig": "In mathematics, the inverse trigonometric functions (occasionally also called antitrigonometric, cyclometric, or arcus functions) are the inverse functions of the trigonometric functions, under suitably restricted domains. Specifically, they are the inverses of the sine, cosine, tangent, cotangent, secant, and cosecant functions, and are used to obtain an angle from any of the angle's trigonometric ratios. Inverse trigonometric functions are widely used in engineering, navigation, physics, and geometry.",
    "complex": "In mathematics, a complex number is an element of a number system that extends the real numbers with a specific element denoted i, called the imaginary unit and satisfying the equation i^2=-1. Since no real number satisfies the above equation, i was called an imaginary number by René Descartes. Every complex number can be expressed in the form a+bi, where a and b are real numbers, a is called the real part, and b is called the imaginary part. The set of complex numbers is denoted by either of the symbols ℂ or C. Despite the historical nomenclature, \"imaginary\" numbers are not fictitious: they are no less real mathematically than real numbers, and they are essential to the scientific description of the physical world.",
    "imaginary": "An imaginary number is the product of a real number and the imaginary unit i, which is defined by its property i^2=-1. The square of an imaginary number bi is -b^2. For example, 5i is an imaginary number, and its square is -25. The number zero is considered to be both real and imaginary.",
    "polar": "In mathematics, the polar coordinate system specifies a given point in a plane by using a distance and an angle as its two coordinates. These are the point's distance from a reference point called the pole, and the point's direction from the pole relative to the direction of the polar axis, a ray drawn from the pole. The distance from the pole is called the radial coordinate, radial distance or simply radius, and the angle is called the angular coordinate, polar angle, or azimuth. The pole is analogous to the origin in a Cartesian coordinate system.",
    "parametric": "In mathematics, a parametric equation expresses several quantities, such as the coordinates of a point, as functions of one or more variables called parameters. In the case of a single parameter, parametric equations are commonly used to express the trajectory of a moving point. For this case, the parameter is often, but not necessarily, time, and the point describes a curve, called a parametric curve. In the case of two parameters, the point describes a surface, called a parametric surface. In all cases, the equations are collectively called a parametric representation, or parametric system, or parameterization (also spelled parametrization, parametrisation) of the object.",
    "vector": "In mathematics and physics, a vector is a generalization of a single number. It may denote a vector quantity, i.e., physical quantity that cannot be expressed by a single scalar quantity. The term may also be used to refer to elements of vector spaces, that can be added together and multiplied (\"scaled\") by scalars. In some contexts, vectors are tuples, which are finite sequences (of numbers or other objects) of a fixed length.",
    "conic": "A conic section, conic or a quadratic curve is a curve obtained from a cone's surface intersecting a plane. The three types of conic section are the hyperbola, the parabola, and the ellipse; the circle is a special case of the ellipse, though it was sometimes considered a fourth type. The ancient Greek mathematicians studied conic sections, culminating around 200 BC with Apollonius of Perga's systematic work on their properties."
}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')    

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "leo" in message.content.lower() or message.author.id == LEO_ID:
        if custom_leo:
            await message.add_reaction(custom_leo)
        await message.channel.send(custom_leo)

    elif "scott" in message.content.lower():
        if custom_scott:
            await message.add_reaction(custom_scott)
        await message.channel.send(custom_scott)

    elif "tsa" in message.content.lower():
        if custom_tsa:
            await message.add_reaction(custom_tsa)
        await message.channel.send(custom_tsa)

    elif "shiv" in message.content.lower():
        await message.channel.send("@shiv")

    elif "game" in message.content.lower():
        await message.channel.send("You just lost the game")

    elif "consty" in message.content.lower() or "consta" in message.content.lower():
        await message.channel.send(file=discord.File('absolute_honors.png'))

    else:
        for key in math_dict:
            if key in message.content.lower():
                await message.channel.send(math_dict[key])
                break

client.run(DISCORD_TOKEN)