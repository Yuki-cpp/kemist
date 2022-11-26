import kemist.core as km


def load_molecules(file):
    molecules = []
    # Consume header
    headers = file.readline().split(";")

    for line in file.readlines():
        columns = line.split(";")

        name = columns[0].strip().lower()

        iupac = columns[1].strip().lower()
        iupac = iupac if iupac != '' else None

        formula = columns[2].strip()
        formula = formula if formula != '' else None

        on_libview = False
        if columns[3] and columns[3].strip().lower() == "yes":
            on_libview = True

        mode = columns[4].strip().lower()

        retention_times = {}
        for i in range(5, len(headers)):
            retention_times[headers[i].strip()] = float(columns[i])

        molecules.append(
            km.Molecule(iupac=iupac, formula=formula, is_on_libview=on_libview, mode=mode, known_names=[name],
                        retention_times=retention_times))
    return molecules


def load_storage_areas(file):
    storages = {}
    file.readline()  # Consume header
    for line in file.readlines():
        columns = line.split(";")

        storage_name = columns[1].strip().lower()
        molecule_name = columns[0].strip().lower()

        if storage_name in storages:
            storages[storage_name].append(km.Molecule(known_names=[molecule_name]))
        else:
            storages[storage_name] = [km.Molecule(known_names=[molecule_name])]

    sto = [km.StorageUnit(name, molecules) for name, molecules in storages.items()]
    return sto
