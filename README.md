# CDP preprocessing

This repository is part of the Pladifes project. 
Things not done yet : 

- virtual env setup (non obligatoire je pense car seulement numpy et pandas mais bon)
- year by year checks
- unexplainable values filtering
- docstrings
- unit tests
- log


- [About CDP preprocessing 💡](#about)
  - [Context](#context)
  - [The Pladifes project](#pladifes)

- [Quickstart 🚀](#quickstart)
  - [Installation ](#installation)
  - [Utilisation](#utilization)


- [Contributing 🤝](#contributing)
- [Contact ✉️](#contact)


# <a id="about"></a> About CGEE

## <a id="context"></a> Context

This project aims to estimate <b>corporate greenhouse gas (GHG) emissions</b> using an open methodology based on state-of-the-art literature.

Corporate GHG emissions are a critical issue for understanding and assessing real company transition strategies effectiveness. It is a key indicator to derive <b>transition risk</b> and <b>impact on climate change</b>. As regulation evolves, it is becoming more and more mandatory for companies to disclose their scope 1, 2 and 3 emissions, but the coverage is far from being close to exhaustivity.

To deal with unreported companies, researchers and practitionners rely on estimated data, ususally from well established data providers. However, these estimates : 
- Often rely on a <b>non-transparent methodology</b>,
- May not always be <b>accurate</b> (usually based on sectorial means),
- Can be <b>expensive</b> (>10k $).

**CGEE** (standing for corporate GHG emissions estimations) address these challenges, by leveraging the latest research and best practices to develop a open data science methodology that allows allow for estimating GHG emissions (Scope1, Scope2, Scope 3 and Scope123) accurately using machine learning.

We plan to release an online calculator on our [dedicated website](https://pladifes.institutlouisbachelier.org/) in 2023 and already give free access to researchers to our <b>complete datasets</b>. 



## <a id="pladifes"></a> Pladifes

Pladifes is a research program aiming at easing the research in green and sustainable finance, as well as traditional one. They are the main authors of <b>CGEE</b>. Learn more about Pladifes [here](https://www.institutlouisbachelier.org/en/pladifes-a-large-financial-and-extra-financial-database-project-2/).

Databases produced in the context of this project are available [here](https://pladifes.institutlouisbachelier.org/data/#ghg-estimations). Other Paldifes databases can be access [here (only ESG)](https://pladifes.institutlouisbachelier.org/data/) and [here (financial and soon ESG)](https://www.eurofidai.org/).

# <a id="quickstart"></a> Quickstart 🚀

## <a id="installation"></a> Installation


You can download a copy of all the files in this repository by cloning the
[git](https://git-scm.com/) repository:

    https://github.com/Pladifes/corporate-ghg-emissions-estimations.git

### Optional: use virtual environment for dependancies management

Preferably, you can use a working Python virtual environment to run the code.
The required dependencies are specified in the file `Pipfile`.
We use `pipenv` virtual environments to manage the project dependencies in
isolation.

Thus, you can install our dependencies without causing conflicts with your
setup (for a Python >= 3.9).
Run the following command in the repository folder (where `Pipfile` and `Pipfile.lock`
is located) to create a separate environment.
Make sure pipenv is installed on your system. You can install it using pip by running:

    pip install pipenv

to install all required dependencies in it:

    pipenv install

Once the installation is complete, activate the virtual environment by running:

    pipenv shell

This will activate the virtual environment and you can start working with your installed dependencies.

## <a id="utilization"></a> Utilization

Code is intended to be easy as easy to use and understand as possible. 
To generate the preprocessed dataset, please directly exectute the main.py file. 
Prefilled parameters are designed for creating a concatenated dataset based on CDP files from years 2015 to 2022 (format : "CDP_CC_emissions data_year.xlsx").

If you want to use this repository for another purpose, please [contact us](mailto:pladifes@institutlouisbachelier.org).

# <a id="contributing"></a> Contributing 🤝

We are hoping that the open-source community will help us edit the code and improve it!

You are welcome to open issues, even suggest solutions and better still contribute the fix/improvement! We can guide you if you're not sure where to start but want to help us out 🥇

In order to contribute a change to our code base, you can submit a pull request (PR) via GitLab and someone from our team will go over it. Yet, we usually prefer that you reach out to us before doing so at [contact](mailto:pladifes@institutlouisbachelier.org).

# <a id="contact"></a> Contact 📝

Maintainers are [Mohamed FAHMAOUI](https://www.linkedin.com/in/mohamed-fahmaoui-b30587176/), [Hamada SALEH](https://www.linkedin.com/in/hamada-saleh-98bb80ab/) and [Thibaud BARREAU](https://www.linkedin.com/in/thibaud-barreau/). CDP preprocessing is developed in the context of the [Pladifes](https://pladifes.institutlouisbachelier.org/) project. If you use Pladifes repositories, models or datasets for academic research, you must mention the following sentence : "Work carried out using resources provided by the Equipex Pladifes (ANR-21-ESRE-0036), hosted by the Institut Louis Bachelier".
