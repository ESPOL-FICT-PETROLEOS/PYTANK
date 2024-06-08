import numpy as np
class OilCorrelations:

    def __init__(self, API, SGsep, Den_sto, P, Pres, Tres, Psep, Tsep, Rsp, Units=1):
        self.API = np.array(API)
        self.SGsep = np.array(SGsep)
        self.Den_sto = np.array(Den_sto)
        self.P = np.array(P)
        self.Pres = np.array(Pres)
        self.Tres = np.array(Tres)
        self.Psep = np.array(Psep)
        self.Tsep = np.array(Tsep)
        self.Rsp = np.array(Rsp)
        self.Units = Units
    def convert_units(self):
        if self.Units == 2:
            self.Den_sto = self.Den_sto / (1.60184634 * 10 ** -2)
            self.P = self.P / (1.45037738 * 10 ** 2)
            self.Pres = self.Pres / (1.45037738 * 10 ** 2)
            self.Tres = (self.Tres * 9 / 5) + 32
            self.Psep = self.Psep / (1.45037738 * 10 ** 2)
            self.Tsep = (self.Tsep * 9 / 5) + 32
            self.Rsp = self.Rsp * (5.61458333)

    def solution_GOR_Pb_ValkoMcCain(self,Psep, Tsep, API, Rsp, Units=1):
        self.convert_units()

        if all(val > 0 for val in [self.Psep, self.Tsep, self.API, self.Rsp]):
            lnPsep = np.log(self.Psep)
            lnTsep = np.log(self.Tsep)

            Zntable = {"VAR1": lnPsep, "C01": -8.005, "C11": 2.7, "C21": -0.161,
                       "VAR2": lnTsep, "C02": 1.224, "C12": -0.5, "C22": 0,
                       "VAR3": self.API, "C03": -1.587, "C13": 0.0441, "C23": -2.29e-5}

            z1 = Zntable["C01"] + (Zntable["C11"] * Zntable["VAR1"]) + (
                        Zntable["C21"] * Zntable["VAR1"] ** 2)
            z2 = Zntable["C02"] + (Zntable["C12"] * Zntable["VAR2"]) + (
                        Zntable["C22"] * Zntable["VAR2"] ** 2)
            z3 = Zntable["C03"] + (Zntable["C13"] * Zntable["VAR3"]) + (
                        Zntable["C23"] * Zntable["VAR3"] ** 2)

            sumZ = z1 + z2 + z3
            Rst = np.exp(3.955 + 0.83 * sumZ - 0.024 * (sumZ ** 2) + (0.075 * (sumZ ** 3)))
            Rsb = Rst + self.Rsp

        elif all(val == 0 for val in [self.Psep, self.Tsep, self.API]) and self.Rsp > 0:
            Rsb = 1.1618 * self.Rsp
        else:
            Rsb = "Incorrect Data"

        if self.Units == 2:
            Rsb = Rsb / (1.78107607 * 10 ** -1)

        return Rsb

    def spec_grav_st_ValkoMcCain2(self):
        self.convert_units()

        if all(val > 0 for val in [self.Psep, self.Tsep, self.API, self.Rsp, self.SGsep]):
            lnPsep = np.log(self.Psep)
            lnRsp = np.log(self.Rsp)

            Zntable = {"VAR1": lnPsep, "C01": -17.275, "C11": 7.9597, "C21": -1.1013,
                       "C31": 2.7735e-2, "C41": 3.2287e-3,
                       "VAR2": lnRsp, "C02": -0.3354, "C12": -0.3346, "C22": 0.1956,
                       "C32": -3.4374e-2, "C42": 2.08e-3,
                       "VAR3": self.API, "C03": 3.705, "C13": -0.4273, "C23": 1.818e-2,
                       "C33": -3.459e-4, "C43": 2.505e-6,
                       "VAR4": self.SGsep, "C04": -155.52, "C14": 629.61, "C24": -957.38,
                       "C34": 647.57, "C44": -163.26,
                       "VAR5": self.Tsep, "C05": 2.085, "C15": -7.097e-2, "C25": 9.859e-4,
                       "C35": -6.312e-6, "C45": 1.4e-8}

            z1 = Zntable["C01"] + (Zntable["C11"] * Zntable["VAR1"]) + (
                        Zntable["C21"] * Zntable["VAR1"] ** 2) + (
                         Zntable["C31"] * Zntable["VAR1"] ** 3) + (
                             Zntable["C41"] * Zntable["VAR1"] ** 4)
            z2 = Zntable["C02"] + (Zntable["C12"] * Zntable["VAR2"]) + (
                        Zntable["C22"] * Zntable["VAR2"] ** 2) + (
                         Zntable["C32"] * Zntable["VAR2"] ** 3) + (
                             Zntable["C42"] * Zntable["VAR2"] ** 4)
            z3 = Zntable["C03"] + (Zntable["C13"] * Zntable["VAR3"]) + (
                        Zntable["C23"] * Zntable["VAR3"] ** 2) + (
                         Zntable["C33"] * Zntable["VAR3"] ** 3) + (
                             Zntable["C43"] * Zntable["VAR3"] ** 4)
            z4 = Zntable["C04"] + (Zntable["C14"] * Zntable["VAR4"]) + (
                        Zntable["C24"] * Zntable["VAR4"] ** 2) + (
                         Zntable["C34"] * Zntable["VAR4"] ** 3) + (
                             Zntable["C44"] * Zntable["VAR4"] ** 4)
            z5 = Zntable["C05"] + (Zntable["C15"] * Zntable["VAR5"]) + (
                        Zntable["C25"] * Zntable["VAR5"] ** 2) + (
                         Zntable["C35"] * Zntable["VAR5"] ** 3) + (
                             Zntable["C45"] * Zntable["VAR5"] ** 4)
            sumZ = z1 + z2 + z3 + z4 + z5

            SGst = 1.219 + 0.198 * sumZ + 0.0845 * (sumZ ** 2) + (0.03 * (sumZ ** 3)) + (
                        0.003 * (sumZ ** 4))
        else:
            SGst = "Incorrect Data"

        return SGst

    def spec_grav_ValkoMcCain2(self):
        self.convert_units()

        if all(val > 0 for val in [self.Psep, self.Tsep, self.API, self.Rsp, self.SGsep]):
            lnPsep = np.log(self.Psep)
            lnTsep = np.log(self.Tsep)

            Zntable = {"VAR1": lnPsep, "C01": -8.005, "C11": 2.7, "C21": -0.161,
                       "VAR2": lnTsep, "C02": 1.224, "C12": -0.5, "C22": 0,
                       "VAR3": self.API, "C03": -1.587, "C13": 0.0441, "C23": -2.29e-5}

            z1 = Zntable["C01"] + (Zntable["C11"] * Zntable["VAR1"]) + (
                        Zntable["C21"] * Zntable["VAR1"] ** 2)
            z2 = Zntable["C02"] + (Zntable["C12"] * Zntable["VAR2"]) + (
                        Zntable["C22"] * Zntable["VAR2"] ** 2)
            z3 = Zntable["C03"] + (Zntable["C13"] * Zntable["VAR3"]) + (
                        Zntable["C23"] * Zntable["VAR3"] ** 2)

            sumZ = z1 + z2 + z3
            Rst = np.exp(3.955 + 0.83 * sumZ - 0.024 * (sumZ ** 2) + (0.075 * (sumZ ** 3)))

            SG = ((self.SGsep * self.Rsp) + (
                        self.spec_grav_st_ValkoMcCain2() * Rst)) / (
                             self.Rsp + Rst)
        elif all(val == 0 for val in [self.Psep, self.Tsep, self.API, self.Rsp]) and self.SGsep > 0:
            SG = 1.066 * self.SGsep
        else:
            SG = "Incorrect Data"

        return SG

    def pb_velarde(self):
        self.convert_units()

        if all(val > 0 for val in [self.API, self.SGsep, self.Tres]):
            lnRsb = np.log(self.solution_GOR_Pb_ValkoMcCain())

            Zntable = {"VAR1": lnRsb, "C01": -5.48, "C11": -0.0378, "C21": 0.281,
                       "C31": -0.0206,
                       "VAR2": self.API, "C02": 1.27, "C12": -0.0449, "C22": 4.36e-4,
                       "C32": -4.76e-6,
                       "VAR3": self.SGsep, "C03": 4.51, "C13": -10.84, "C23": 8.39,
                       "C33": -2.34,
                       "VAR4": self.Tres, "C04": -0.7835, "C14": 6.23e-3, "C24": -1.22e-5,
                       "C34": 1.03e-8}

            z1 = Zntable["C01"] + (Zntable["C11"] * Zntable["VAR1"]) + (
                    Zntable["C21"] * Zntable["VAR1"] ** 2) + (
                         Zntable["C31"] * Zntable["VAR1"] ** 3)
            z2 = Zntable["C02"] + (Zntable["C12"] * Zntable["VAR2"]) + (
                    Zntable["C22"] * Zntable["VAR2"] ** 2) + (
                         Zntable["C32"] * Zntable["VAR2"] ** 3)
            z3 = Zntable["C03"] + (Zntable["C13"] * Zntable["VAR3"]) + (
                    Zntable["C23"] * Zntable["VAR3"] ** 2) + (
                         Zntable["C33"] * Zntable["VAR3"] ** 3)
            z4 = Zntable["C04"] + (Zntable["C14"] * Zntable["VAR4"]) + (
                    Zntable["C24"] * Zntable["VAR4"] ** 2) + (
                         Zntable["C34"] * Zntable["VAR4"] ** 3)
            sumZ = z1 + z2 + z3 + z4

            Pb = np.exp(7.475 + 0.713 * sumZ + 0.0075 * (sumZ ** 2))

        else:
            Pb = "Missing Data"

        if self.Units == 1:
            return Pb
        else:
            return Pb * (6.89475729 * 10 ** -3)

    def solution_GOR_Velarde2(self):

        if all(val > 0 for val in [self.API, self.SGsep, self.Tres, self.P]) and self.P < self.pb_velarde():

            Pr = (self.P - 14.7) / (self.pb_velarde() - 14.7)

            antable = {"A0": 9.73e-7, "B0": 0.022339, "C0": 0.725167,
                       "A1": 1.672608, "B1": -1.00475, "C1": -1.485480,
                       "A2": 0.92987, "B2": 0.337711, "C2": -0.164741,
                       "A3": 0.247235, "B3": 0.132795, "C3": -0.09133,
                       "A4": 1.056052, "B4": 0.302065, "C4": 0.047094}

            a1 = antable["A0"] * self.SGsep ** antable["A1"] * self.API ** antable[
                "A2"] * self.Tres ** antable["A3"] * (
                         self.pb_velarde() - 14.7) ** antable[
                     "A4"]
            a2 = antable["B0"] * self.SGsep ** antable["B1"] * self.API ** antable[
                "B2"] * self.Tres ** antable["B3"] * (
                         self.pb_velarde() - 14.7) ** antable[
                     "B4"]
            a3 = antable["C0"] * self.SGsep ** antable["C1"] * self.API ** antable[
                "C2"] * self.Tres ** antable["C3"] * (
                         self.pb_velarde() - 14.7) ** antable[
                     "C4"]

            Rsr = (a1 * Pr ** a2) + ((1 - a1) * Pr ** a3)
            Rs = self.solution_GOR_Pb_ValkoMcCain() * Rsr

        elif self.P >= self.pb_velarde():
            Rs = 0
        else:
            Rs = "Missing Data"

        if self.Units == 1:
            return Rs
        else:
            return Rs / (1.78107607 * 10 ** -1)

    def Co_above_Pb_Spivey1(self):
        self.convert_units()

        if all(val > 0 for val in [self.API, self.SGsep, self.Tres, self.P]):
            Pr = (self.P - 14.7) / (self.pb_velarde() - 14.7)

            lnAPI = np.log(self.API)
            lnSGsep = np.log(self.SGsep)
            lnPb = np.log(self.pb_velarde())
            lnPr = np.log(Pr)
            lnRsb = np.log(self.solution_GOR_Pb_ValkoMcCain())
            lnTres = np.log(self.Tres)

            Zntable = {"VAR1": lnAPI, "C01": 3.011, "C11": -2.6254, "C21": 0.497,
                       "VAR2": lnSGsep, "C02": -0.0835, "C12": -0.259, "C22": 0.382,
                       "VAR3": lnPb, "C03": 3.51, "C13": -0.0289, "C23": -0.0584,
                       "VAR4": lnPr, "C04": 0.327, "C14": -0.608, "C24": 0.0911,
                       "VAR5": lnRsb, "C05": -1.918, "C15": -0.642, "C25": 0.154,
                       "VAR6": lnTres, "C06": 2.52, "C16": -2.73, "C26": 0.429}

            z1 = Zntable["C01"] + (Zntable["C11"] * Zntable["VAR1"]) + (
                    Zntable["C21"] * Zntable["VAR1"] ** 2)
            z2 = Zntable["C02"] + (Zntable["C12"] * Zntable["VAR2"]) + (
                    Zntable["C22"] * Zntable["VAR2"] ** 2)
            z3 = Zntable["C03"] + (Zntable["C13"] * Zntable["VAR3"]) + (
                    Zntable["C23"] * Zntable["VAR3"] ** 2)
            z4 = Zntable["C04"] + (Zntable["C14"] * Zntable["VAR4"]) + (
                    Zntable["C24"] * Zntable["VAR4"] ** 2)
            z5 = Zntable["C05"] + (Zntable["C15"] * Zntable["VAR5"]) + (
                    Zntable["C25"] * Zntable["VAR5"] ** 2)
            z6 = Zntable["C06"] + (Zntable["C16"] * Zntable["VAR6"]) + (
                    Zntable["C26"] * Zntable["VAR6"] ** 2)

            sumZ = z1 + z2 + z3 + z4 + z5 + z6

            Cofb = np.exp(2.434 + (0.475 * sumZ) + (0.048 * sumZ ** 2) - np.log(10 ** 6))

        else:
            Cofb = "Missing Data"

        if self.Units == 1:
            return Cofb
        else:
            return Cofb / (1.45037738 * 10 ** 2)

    def Co_above_Pb_Spivey2(self):
        self.convert_units()

        if all(val > 0 for val in [self.Pres, self.P]):
            Pri = (self.Pres - 14.7) / (self.pb_velarde() - 14.7)

            lnAPI = np.log(self.API)
            lnSGsep = np.log(self.SGsep)
            lnPb = np.log(self.pb_velarde())
            lnPri = np.log(Pri)
            lnRsb = np.log(self.solution_GOR_Pb_ValkoMcCain())
            lnTres = np.log(self.Tres)

            Zntable = {"VAR1": lnAPI, "C01": 3.011, "C11": -2.6254, "C21": 0.497,
                       "VAR2": lnSGsep, "C02": -0.0835, "C12": -0.259, "C22": 0.382,
                       "VAR3": lnPb, "C03": 3.51, "C13": -0.0289, "C23": -0.0584,
                       "VAR4": lnPri, "C04": 0.327, "C14": -0.608, "C24": 0.0911,
                       "VAR5": lnRsb, "C05": -1.918, "C15": -0.642, "C25": 0.154,
                       "VAR6": lnTres, "C06": 2.52, "C16": -2.73, "C26": 0.429}

            z1 = Zntable["C01"] + (Zntable["C11"] * Zntable["VAR1"]) + (
                    Zntable["C21"] * Zntable["VAR1"] ** 2)
            z2 = Zntable["C02"] + (Zntable["C12"] * Zntable["VAR2"]) + (
                    Zntable["C22"] * Zntable["VAR2"] ** 2)
            z3 = Zntable["C03"] + (Zntable["C13"] * Zntable["VAR3"]) + (
                    Zntable["C23"] * Zntable["VAR3"] ** 2)
            z4 = Zntable["C04"] + (Zntable["C14"] * Zntable["VAR4"]) + (
                    Zntable["C24"] * Zntable["VAR4"] ** 2)
            z5 = Zntable["C05"] + (Zntable["C15"] * Zntable["VAR5"]) + (
                    Zntable["C25"] * Zntable["VAR5"] ** 2)
            z6 = Zntable["C06"] + (Zntable["C16"] * Zntable["VAR6"]) + (
                    Zntable["C26"] * Zntable["VAR6"] ** 2)

            sumZ = z1 + z2 + z3 + z4 + z5 + z6

            Cofbi = np.exp(2.434 + (0.475 * sumZ) + (0.048 * sumZ ** 2) - np.log(10 ** 6))

            Cofi = (self.pb_velarde() * self.Co_above_Pb_Spivey1() - (
                            self.pb_velarde() * Cofbi)) / (self.Pres - self.P)
        else:
            Cofi = "Missing Data"

        if self.Units == 1:
            Cofi = Cofi

        else:
            Cofi = Cofi / (1.45037728 * 10 ** 2)

        return Cofi

    def Co_above_Pb_Spivey3(self):
        self.convert_units()

        if all(val > 0 for val in [self.P]):
            Pr = (self.P - 14.7) / (self.pb_velarde() - 14.7)

            dZdP = (-0.608 + (0.1822 * np.log(
                self.P / self.pb_velarde()))) / self.P

            lnAPI = np.log(self.API)
            lnSGsep = np.log(self.SGsep)
            lnPb = np.log(self.pb_velarde())
            lnPr = np.log(Pr)
            lnRsb = np.log(self.solution_GOR_Pb_ValkoMcCain())
            lnTres = np.log(self.Tres)

            Zntable = {"VAR1": lnAPI, "C01": 3.011, "C11": -2.6254, "C21": 0.497,
                       "VAR2": lnSGsep, "C02": -0.0835, "C12": -0.259, "C22": 0.382,
                       "VAR3": lnPb, "C03": 3.51, "C13": -0.0289, "C23": -0.0584,
                       "VAR4": lnPr, "C04": 0.327, "C14": -0.608, "C24": 0.0911,
                       "VAR5": lnRsb, "C05": -1.918, "C15": -0.642, "C25": 0.154,
                       "VAR6": lnTres, "C06": 2.52, "C16": -2.73, "C26": 0.429}

            z1 = Zntable["C01"] + (Zntable["C11"] * Zntable["VAR1"]) + (
                    Zntable["C21"] * Zntable["VAR1"] ** 2)
            z2 = Zntable["C02"] + (Zntable["C12"] * Zntable["VAR2"]) + (
                    Zntable["C22"] * Zntable["VAR2"] ** 2)
            z3 = Zntable["C03"] + (Zntable["C13"] * Zntable["VAR3"]) + (
                    Zntable["C23"] * Zntable["VAR3"] ** 2)
            z4 = Zntable["C04"] + (Zntable["C14"] * Zntable["VAR4"]) + (
                    Zntable["C24"] * Zntable["VAR4"] ** 2)
            z5 = Zntable["C05"] + (Zntable["C15"] * Zntable["VAR5"]) + (
                    Zntable["C25"] * Zntable["VAR5"] ** 2)
            z6 = Zntable["C06"] + (Zntable["C16"] * Zntable["VAR6"]) + (
                    Zntable["C26"] * Zntable["VAR6"] ** 2)

            sumZ = z1 + z2 + z3 + z4 + z5 + z6

            dCofbdP = self.Co_above_Pb_Spivey1() * (
                    (0.475 + (0.096 * sumZ)) * dZdP)
            Co = self.Co_above_Pb_Spivey1() + (
                    (self.P - self.pb_velarde()) * dCofbdP)

        else:
            Co = "Missing Data"

        if self.Units == 1:
            Co = Co

        else:
            Co = Co / (1.45037728 * 10 ** 2)

        return Co

    def den_pb(self):
        self.convert_units()

        Den_pseudo1 = 52.8 - (0.01 * (self.solution_GOR_Pb_ValkoMcCain()))

        if all(val > 0 for val in [self.SGsep, self.Tres]):

            antable = {"a0": -49.8930, "a1": 85.0149, "a2": -3.70373, "a3": 0.0479818,
                       "a4": 2.98914, "a5": -0.0356888}

            den_ap = antable["a0"] + antable["a1"] * self.SGsep + antable[
                "a2"] * self.SGsep * Den_pseudo1 + antable[
                         "a3"] * self.SGsep * Den_pseudo1 ** 2 + antable[
                         "a4"] * Den_pseudo1 + antable["a5"] * Den_pseudo1 ** 2

            Den_pseudo2 = (self.solution_GOR_Pb_ValkoMcCain() * self.spec_grav_ValkoMcCain2()) + (
                    4600 * (self.spec_grav_st_ValkoMcCain2())) / (73.71 + (
                (self.solution_GOR_Pb_ValkoMcCain() * self.spec_grav_ValkoMcCain2())))

            while ((abs(Den_pseudo1 - Den_pseudo2)) / Den_pseudo2) > 0.1:

                Den_pseudo1 = Den_pseudo2

                den_ap = antable["a0"] + antable["a1"] * self.SGsep + antable[
                    "a2"] * self.SGsep * Den_pseudo1 + antable[
                             "a3"] * self.SGsep * Den_pseudo1 ** 2 + antable[
                             "a4"] * Den_pseudo1 + antable["a5"] * Den_pseudo1 ** 2

                Den_pseudo2 = ((self.solution_GOR_Pb_ValkoMcCain() * self.spec_grav_ValkoMcCain2()) + (
                                       4600 * self.spec_grav_st_ValkoMcCain2())) / (
                                      73.71 + (
                                      (self.solution_GOR_Pb_ValkoMcCain() * self.spec_grav_ValkoMcCain2()) / den_ap))

                if ((abs(Den_pseudo1 - Den_pseudo2)) / Den_pseudo2) < 0.1:
                    break

            den_adjP = ((0.167 + 16.181 * (10 ** (-0.0425 * Den_pseudo2))) * (
                    self.pb_velarde() / 1000)) - 0.01 * (
                               (0.299 + 263 * (10 ** (-0.0603 * Den_pseudo2))) * (
                               self.pb_velarde() / 1000) ** 2)

            den_fake = den_adjP + Den_pseudo2

            den_adjT = ((0.00302 + (1.505 * den_fake ** -0.951)) * (
                    (self.Tres - 60) ** 0.938)) - (
                               (0.0216 - 0.0233 * (10 ** (-0.0161 * den_fake))) * (
                               (self.Tres - 60) ** 0.475))

            den_Pb = den_fake - den_adjT

        if self.Units == 1:
            den_Pb = den_Pb

        else:
            den_Pb = den_Pb / (1.60184634 * 10 ** -2)

        return den_Pb

    def den_underpb(self):
        self.convert_units()

        Den_pseudo1 = 52.8 - (0.01 * (self.solution_GOR_Velarde2()))

        if all(val > 0 for val in [self.SGsep, self.Tres]):

            antable = {"a0": -49.8930, "a1": 85.0149, "a2": -3.70373, "a3": 0.0479818,
                       "a4": 2.98914, "a5": -0.0356888}

            den_ap = antable["a0"] + antable["a1"] * self.SGsep + antable[
                "a2"] * self.SGsep * Den_pseudo1 + antable[
                         "a3"] * self.SGsep * Den_pseudo1 ** 2 + antable[
                         "a4"] * Den_pseudo1 + antable["a5"] * Den_pseudo1 ** 2

            Den_pseudo2 = (self.solution_GOR_Velarde2() * self.spec_grav_ValkoMcCain2() + (
                    4600 * self.spec_grav_st_ValkoMcCain2())) / (
                                  73.71 + (self.solution_GOR_Velarde2() * self.spec_grav_st_ValkoMcCain2() / den_ap))

            while ((abs(Den_pseudo1 - Den_pseudo2)) / Den_pseudo2) * 100 > 10:

                Den_pseudo1 = Den_pseudo2

                den_ap = antable["a0"] + antable["a1"] * self.SGsep + antable[
                    "a2"] * self.SGsep * Den_pseudo1 + antable[
                             "a3"] * self.SGsep * Den_pseudo1 ** 2 + antable[
                             "a4"] * Den_pseudo1 + antable["a5"] * Den_pseudo1 ** 2

                Den_pseudo2 = ((self.solution_GOR_Velarde2() * self.spec_grav_ValkoMcCain2()) + (
                                       4600 * self.spec_grav_st_ValkoMcCain2())) / (
                                      73.71 + ((self.solution_GOR_Velarde2() * self.spec_grav_ValkoMcCain2()) / den_ap))

                if ((abs(Den_pseudo1 - Den_pseudo2)) / Den_pseudo2) < 0.1:
                    break

            den_adjP = ((0.167 + 16.181 * (10 ** (-0.0425 * Den_pseudo2))) * (
                    self.P / 1000)) - 0.01 * (
                               (0.299 + 263 * (10 ** (-0.0603 * Den_pseudo2))) * (
                               self.P / 1000) ** 2)

            den_fake = den_adjP + Den_pseudo2

            den_adjT = ((0.00302 + (1.505 * den_fake ** -0.951)) * (
                    (self.Tres - 60) ** 0.938)) - (
                               (0.0216 - 0.0233 * (10 ** (-0.0161 * den_fake))) * (
                               (self.Tres - 60) ** 0.475))

            den_underPb = den_fake - den_adjT

        if self.Units == 1:
            den_underPb = den_underPb

        else:
            den_underPb = den_underPb / (1.60184634 * 10 ** -2)

        return den_underPb

    def den_abovepb(self):
        self.convert_units()

        den_abovePb = self.den_pb() * np.exp(
            self.Co_above_Pb_Spivey1() * (
                    self.P - self.pb_velarde()))

        if self.Units == 1:
            den_abovePb = den_abovePb

        else:
            den_abovePb = den_abovePb / (1.60184634 * 10 ** -2)

        return den_abovePb

    def FVF_pb(self):
        self.convert_units()

        Bob = (self.Den_sto + (
                0.01357 * self.solution_GOR_Pb_ValkoMcCain() * self.spec_grav_st_ValkoMcCain2())) / self.den_pb()

        return Bob

    def FVF_underpb(self):
        self.convert_units()

        Bo_underPb = (self.Den_sto + (
                0.01357 * self.solution_GOR_Velarde2() * self.spec_grav_st_ValkoMcCain2())) / self.den_underpb()

        return Bo_underPb

    def FVF_abovepb(self):
        self.convert_units()

        Bo_abovePb = self.FVF_pb() * np.exp(
            self.Co_above_Pb_Spivey1() * (self.pb_velarde() - self.P))

        return Bo_abovePb

    def viscosity_pb(self):
        self.convert_units()

        C = (10 ** (3.0324 - 0.02023 * self.API)) * (self.Tres ** -1.163)

        uoD = (10 ** C) - 1

        A = 10.715 * (self.solution_GOR_Pb_ValkoMcCain() + 100) ** -0.515
        B = 5.44 * (self.solution_GOR_Pb_ValkoMcCain() + 150) ** -0.338

        uob = A * uoD ** B

        if self.Units == 1:
            uob = uob

        else:
            uob = uob / (0.001)

        return uob

    def viscosity_underpb(self):
        self.convert_units()

        A = 10.715 * (self.solution_GOR_Velarde2() + 100) ** -0.515
        B = 5.44 * (self.solution_GOR_Velarde2() + 150) ** -0.338

        C = (10 ** (3.0324 - 0.02023 * self.API)) * (self.Tres ** -1.163)

        uoD = (10 ** C) - 1

        uoR = A * uoD ** B

        if self.Units == 1:
            uoR = uoR

        else:
            uoR = uoR / (0.001)

        return uoR

    def viscosity_abovepb(self):
        self.convert_units()

        A = -1.0146 + (1.3322 * np.log10(self.viscosity_pb())) - (
                0.4876 * (np.log10(self.viscosity_pb())) ** 2) - (
                    1.15036 * (np.log10(self.viscosity_pb())) ** 3)

        uoR = self.viscosity_pb() + ((1.3449 * 10 ** -3) * (
                self.P - self.pb_velarde()) * 10 ** A)

        if self.Units == 1:
            uoR = uoR

        else:
            uoR = uoR / (0.001)

        return uoR

