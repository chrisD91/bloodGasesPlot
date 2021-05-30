import bloodGases2 as bg
import copy
import csv


def loadDataFile(file):
    global gases, gasesV
    # reset the lists and add a reference
    gases, gasesV = [], {}
    g0 = bg.Gas()
    gases.append(g0)
    gasesV["g0"] = g0

    # titles = ['spec', 'hb', 'fio2', 'po2', 'ph', 'pco2', 'hco3']
    default = ["horse", 12, 0.21, 100, 7.4, 40, 24]
    # load the data
    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
        next(reader, None)  # skip the firstLine
        k = 1
        for row in reader:
            for i, item in enumerate(row):
                row[i] = row[i].replace(",", ".")
                row[i] = row[i].replace(" ", "")
                # replace empty spec
                if len(row[0]) == 0:
                    row[0] = "dog"
                # tranform string to floats
                if i > 0:
                    try:
                        dec = row[i]
                        dec = float(dec)
                        row[i] = dec
                    except ValueError:
                        # print('i=', i, ' ', item, ' row[i]=', row[i],
                        #    type(row[i]), 'len=',len(row[i]))
                        row[i] = None
                    if row[i] in (None, ""):
                        row[i] = default[i]
            # implement variables
            spec = row[0]
            hb = row[1]
            fio2 = row[2]
            po2 = row[3]
            ph = row[4]
            pco2 = row[5]
            hco3 = row[6]
            # build gasObj
            sample = bg.Gas(spec, hb, fio2, po2, ph, pco2, hco3)
            gases.append(copy.deepcopy(sample))
            name = "g" + str(k)
            gasesV[name] = sample.__dict__
            k += 1
            # print ('spec=', spec, 'hb=', hb ,'fio2=', fio2, 'po2=', po2,
            #         'ph=', ph, 'pco2=', pco2, 'hco3=', hco3)
            # print ('spec=', type(spec), 'hb=', type(hb) ,'fio2=', type(fio2), 'po2=', type(po2),
            #         'ph=', type(ph), 'pco2=', type(pco2), 'hco3=', type(hco3))

        print("added ", len(gases), "gases to gases and gasesV")


loadDataFile("example.csv")
