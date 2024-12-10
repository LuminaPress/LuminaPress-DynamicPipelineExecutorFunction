from text.generators.title_generator import ElegantTitleGenerator

title_generator = ElegantTitleGenerator()
print(
    title_generator.generate_elegant_title(
        [
            "Apple employee has sued due to them accusing apple of spying on them through their own network of phone communcations and a lawsuit has been filed regarding it."
        ]
    )
)
