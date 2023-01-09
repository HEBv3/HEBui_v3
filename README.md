# About HEBui_v3.0

The **py3CSEP HEB** is the python implementation of the **3CSEP High Efficiency Buildings (HEB)** model developed by the [*Department of Environmental Sciences and Policy*](https://envsci.ceu.edu/) at [**CEU**](https://www.ceu.edu/) (Central European University).

This module (HEBui_v3.0) serves the access (and basic visualization) of the model data. It was developed by Benedek Kiss and Zoltán Hajnal in the framework of the EU-H2020 research project [SENTINEL](https://sentinel.energy/).

This software uses open-source packages.

# Documentation

Detailed description of the model can be found in the published research reports, the most essential ones also included in the [*`documentation`*](https://github.com/HEBv3/HEBui_v3/tree/main/documentation) folder.

## How to cite the HEB model

In derived works, please cite the HEB model as:

**Decarbonisation Pathways for Buildings**, *Souran Chatterjee, Benedek Kiss, Diana Ürge-Vorsatz & Sven Teske*, pp 161–185 in: Achieving the Paris Climate Agreement Goals Part 2 (ed. Sven Teske), DOI 10.1007/978-3-030-99177-7, [https://doi.org/10.1007/978-3-030-99177-7](https://doi.org/10.1007/978-3-030-99177-7)


# Input data

The input data of the model (the buildings' categorization scheme, as well as preprocessed background data derived from several international statistical, economic, and demographic databases) can be found in the [*`input_data`*](https://github.com/HEBv3/HEBui_v3/tree/main/input_data) folder.

# Downloading HEBui

The HEBui package is made available via GitHub: [https://github.com/HEBv3/HEBui_v3](https://github.com/HEBv3/HEBui_v3).

To download the package, follow the above link, and in the upper right corner of the folder listing find the (green) **[<> Code]** button. Pressing it, you can select ***Download ZIP*** from the dropdown menu.

# Software requirements

- HEBui was written in *python*, thus some *python* distribution needs to be installed on a system to be able to run it.
- Also, some additional (open source) packages are used by the software, which are listed in the [*`requirements.txt`*](https://github.com/HEBv3/HEBui_v3/blob/main/HEBui/requirements.txt) file (in the *`HEBui`* folder).
- For the installation of the above, prior to running the *`HEBui`*, please refer to the documention of your *python* distribution & environment.

# Unpacking & Running HEBui

- Unpack the ZIP file contents to a folder of your choice (named *`[HEBmain]`* in the following)
- Open a terminal for command line access (on windows systems, e.g. *`cmd.exe`*)
- Navigate to the *`[HEBmain]/HEBui`* folder (on windows systems: *`[HEBmain]\HEBui`*)
- Run the following command: *`python hebui_v3_0.py`*
- The terminal shows basic messages of a local (minimal) *web-server* starting-up
- In a web-browser (like *Firefox*) open a new window/tab, and type in the address bar: *`localhost:8050`* -- with this, the greeting panel of pyHEB should open
- After finishing (closing the web-browser window/tab) the program can be interrupted/closed by pressing *`ctrl+C`* (or *`ctrl-BREAK`* on windows systems) in the terminal

# Output

After selecting the options for the scenarios (or just using the initial values) the *`Calculate`* tab  offers a **`[Calculation:]`** button. Pressing it prepares the model output in several data tables for the scenarios, that can be downloaded in *CSV* format for further analysis. The tables' header codes can be interpreted as follows:

## LID: location ID

(file: [*`LID.csv`*](https://github.com/HEBv3/HEBui_v3/blob/main/input_data/LID.csv))

| LID | Label | location (country) name |
| --- | ----- | ----------------------- |
| 15 | AUT | Austria |
| 16 | BEL | Belgium |
| 17 | BGR | Bulgaria |
| 18 | CYP | Cyprus |
| 19 | CZE | Czech Republic |
| 20 | DEU | Germany |
| 21 | DNK | Denmark |
| 22 | ESP | Spain |
| 23 | EST | Estonia |
| 24 | FIN | Finland |
| 25 | FRA | France |
| 26 | GBR | United Kingdom |
| 27 | GRC | Greece |
| 28 | HUN | Hungary |
| 29 | IRL | Ireland |
| 30 | ITA | Italy |
| 31 | LTU | Lithuania |
| 32 | LUX | Luxembourg |
| 33 | LVA | Latvia |
| 34 | MLT | Malta |
| 35 | NLD | Netherlands |
| 36 | POL | Poland |
| 37 | PRT | Portugal |
| 38 | ROU | Romania |
| 39 | SVK | Slovakia |
| 40 | SVN | Slovenia |
| 41 | SWE | Sweden |
| 42 | HRV | Croatia |

## CID: climate ID

(file: [*`CID.csv`*](https://github.com/HEBv3/HEBui_v3/blob/main/input_data/CID.csv))

| CID | description |
| :-- | :---------- |
| 1 | Only heating (Very high heating demand) |
| 2 | Only heating (High heating demand) |
| 3 | Only heating (Moderate heating demand) |
| 4 | Only heating (Low heating demand) |
| 5 | Heating and cooling (High heating and low cooling demand) |
| 6 | Heating and cooling (Moderate heating and low cooling demand) |
| 7 | Heating and cooling (Moderate heating and moderate cooling demand) |
| 8 | Heating and cooling (Low heating and high cooling demand) |
| 9 | Heating and cooling (Low heating and moderate cooling demand) |
| 10 | Heating and cooling (Low heating and low cooling demand) |
| 11 | Only cooling (Very high cooling demand) |
| 12 | Only cooling (High cooling demand) |
| 13 | Only cooling (Moderate cooling demand) |
| 14 | Only cooling (Low cooling demand) |
| 15 | Cooling and dehumidification (High cooling demand) |
| 16 | Cooling and dehumidification (Moderate cooling demand) |
| 17 | Cooling and dehumidification (Low cooling demand) |
| 18 | "Heating, cooling and dehumidification (Low and moderate heating and cooling demand)" |
| 19 | Minor heating and cooling (Low heating and moderate cooling demand) |

## UID: urbanization ID

(file: [*`UID.csv`*](https://github.com/HEBv3/HEBui_v3/blob/main/input_data/UID.csv))

| UID | Label | FullName |
| --- | ----- | -------- |
| 1 | URB | Urban |
| 2 | RUR | Rural |

## BCID: building category ID

(file: [*`BCID.csv`*](https://github.com/HEBv3/HEBui_v3/blob/main/input_data/BCID.csv))

| BCID | Label | FullName |
| :--- | :---- | :------- |
| 1 | RESI | Residential |
| 2 | COMM | Commercial&Public |
| 3 | SLUM | Slum |

## BTID: building type ID

(file: [*`BTID.csv`*](https://github.com/HEBv3/HEBui_v3/blob/main/input_data/BTID.csv))

| BTID | Label | FullName | BCID |
| :--- | :---- | :------- | :--- |
| 1 | EDUC | Educational buildings | 2 |
| 2 | HORES | Hotels & Restaurants | 2 |
| 3 | HOSP | Hospitals | 2 |
| 4 | OTHER | Others | 2 |
| 5 | RETAIL | Retails | 2 |
| 6 | OFFICE | Offices | 2 |
| 7 | SF | Single-family | 1 |
| 8 | MF | Multi-family | 1 |
| 9 | SLUM | Slum | 3 |

## VID: building vintage ID

(file: [*`VID.csv`*](https://github.com/HEBv3/HEBui_v3/blob/main/input_data/VID.csv))

| VID | Label | FullName |
| :-- | :---- | :------- |
| 1 | st | standard |
| 2 | ret | retrofitted |
| 3 | aret | advanced retrofitted |
| 4 | new | new |
| 5 | anew | advanced new |

# License

The **HEBui source code** consists of the *hebui_v3_0.py* file, its packaged data files in the *data/* folder, and input data collection of the *input_data* folder, licensed under the GNU Affero General Public License:

    Copyright (C) 2022 - [Central European University](https://www.ceu.edu/)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
