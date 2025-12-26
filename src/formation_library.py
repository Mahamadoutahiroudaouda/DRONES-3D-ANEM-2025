import numpy as np

class FormationLibrary:
    def __init__(self):
        # Palette Officielle
        self.colors = {
            "orange_niger": [1.0, 0.5, 0.0],    # Golden Orange for Desert
            "blanc_pure": [1.0, 1.0, 1.0],      
            "vert_niger": [0.0, 0.6, 0.2],  
            "soleil_or": [1.0, 0.84, 0.0],      # Gold
            "bleu_nuit": [0.0, 0.122, 0.247],   
            "turquoise": [0.224, 0.8, 0.8],
            "star_white": [0.95, 0.95, 1.0],   # Cold Star White
            "star_blue": [0.7, 0.85, 1.0],     # Twinkling Sky Blue
        }
        
        # Precise Niger Boundary (extracted from GeoJSON)
        # Simplified to main boundary for performance
        self.niger_coords = [
            [3.2725,11.9626],[3.2688,11.9729],[3.2625,11.9824],[3.2486,11.9942],[3.2606,12.0116],[3.2618,12.0162],[3.2386,12.0335],[3.2347,12.0383],[3.2325,12.0475],[3.2203,12.0608],
            [3.2061,12.0692],[3.1889,12.0836],[3.1764,12.1058],[3.1686,12.1136],[3.1272,12.1403],[3.1278,12.1544],[3.125,12.1575],[3.1139,12.1628],[3.1008,12.1725],[3.0822,12.1767],
            [3.0719,12.1836],[3.0597,12.1961],[3.0581,12.2017],[3.06,12.2061],[3.0592,12.2086],[3.0297,12.2336],[3.0253,12.2408],[3.0194,12.2572],[3.0136,12.2664],[2.9936,12.2766],
            [2.9814,12.2859],[2.9585,12.2945],[2.9444,12.3167],[2.9414,12.3183],[2.9272,12.335],[2.9219,12.3367],[2.9069,12.3494],[2.8869,12.3707],[2.8844,12.3772],[2.8811,12.3781],
            [2.8725,12.3878],[2.8465,12.4004],[2.8389,12.4067],[2.8325,12.4075],[2.8192,12.4137],[2.8058,12.4174],[2.7946,12.4184],[2.7752,12.411],[2.7329,12.3622],[2.7288,12.3626],
            [2.4668,12.011],[2.4336,11.9588],[2.4114,11.9063],[2.3717,11.9414],[2.0645,12.3611],[2.0917,12.3938],[2.1261,12.3986],[2.1552,12.42],[2.1865,12.4216],[2.224,12.4227],
            [2.2712,12.4678],[2.2259,12.583],[2.1108,12.7069],[2.0131,12.7284],[1.6833,12.6246],[1.4105,12.7633],[1.202,12.936],[1.1234,12.9995],[0.9916,13.108],[1.0188,13.3722],
            [1.2044,13.3495],[1.283,13.3523],[1.1561,13.4127],[1.0408,13.4831],[0.9736,13.5758],[0.9071,13.6187],[0.7845,13.6735],[0.6053,13.7098],[0.6256,13.7653],[0.5847,13.7949],
            [0.5262,13.8664],[0.4716,13.9299],[0.4832,13.9513],[0.4505,13.9566],[0.4105,14.011],[0.3951,14.0863],[0.357,14.1484],[0.3869,14.222],[0.4038,14.2497],[0.3859,14.2887],
            [0.3229,14.362],[0.2666,14.3905],[0.2146,14.4494],[0.1768,14.4924],[0.2312,14.7217],[0.2357,14.8861],[0.2294,14.9897],[0.5043,15.0],[0.6094,14.9702],[0.7191,14.959],
            [0.9732,14.9789],[1.211,15.1765],[1.3111,15.2596],[1.3893,15.2712],[1.5576,15.2817],[1.9189,15.3083],[2.4991,15.3579],[2.9181,15.3511],[3.2611,15.3416],[3.4099,15.3405],
            [3.5275,15.3415],[3.5377,15.43],[3.6077,15.5262],[3.7215,15.6482],[3.8379,15.6696],[3.8891,15.717],[3.9117,15.8449],[3.9473,15.9415],[4.0045,15.9956],[4.0768,16.9123],
            [4.2412,16.9877],[4.2395,17.6514],[4.2432,18.5637],[4.3362,19.1566],[5.8171,19.4377],[6.198,19.7747],[6.6905,20.2102],[7.184,20.6353],[7.5591,20.9128],[8.4083,21.4278],
            [9.5753,22.1295],[10.1396,22.4586],[11.1201,23.0346],[11.9796,23.525],[12.1219,23.4895],[12.4348,23.4221],[12.6227,23.3819],[12.7897,23.3471],[13.0295,23.2949],[13.199,23.2603],
            [13.3833,23.2178],[13.4806,23.1861],[13.5447,23.157],[13.6937,23.0597],[13.7764,22.9922],[13.9222,22.8669],[14.0609,22.7516],[14.1893,22.6445],[14.4155,22.7468],[14.6124,22.8325],
            [14.7033,22.8741],[14.8659,22.9444],[14.9015,22.9606],[14.9959,23.0019],[15.0296,22.8449],[15.1144,22.4048],[15.1479,22.2383],[15.194,21.8452],[15.1972,21.5322],[15.1984,21.4913],
            [15.3012,21.4119],[15.4842,21.1595],[15.6256,20.9632],[15.5488,20.8669],[15.6405,20.7228],[15.8652,20.4625],[15.9956,20.3485],[15.7536,19.9478],[15.7458,19.9107],[15.7286,19.772],
            [15.7276,19.7582],[15.7169,19.6772],[15.7081,19.6176],[15.6981,19.5387],[15.6792,19.385],[15.6762,19.359],[15.6584,19.2244],[15.6536,19.1909],[15.6403,19.094],[15.6343,19.0408],
            [15.6153,18.8913],[15.612,18.8688],[15.6025,18.7977],[15.5983,18.7661],[15.5897,18.6388],[15.5877,18.5963],[15.5736,18.3189],[15.565,18.1464],[15.5594,18.0062],[15.5534,17.8838],
            [15.5531,17.8425],[15.5451,17.7076],[15.5384,17.61],[15.5247,17.31],[15.5202,17.2413],[15.5184,17.1736],[15.5141,17.1017],[15.5099,17.0095],[15.5083,16.9737],[15.5055,16.8979],
            [15.3304,16.715],[15.26,16.6427],[15.2191,16.5981],[14.9136,16.2766],[14.8172,16.1758],[14.6384,15.9914],[14.6104,15.956],[14.5554,15.9037],[14.5148,15.8622],[14.3926,15.7378],
            [14.3185,15.6441],[14.3062,15.6245],[14.2357,15.5354],[14.123,15.3754],[14.1056,15.3497],[14.0475,15.2701],[14.0357,15.2485],[13.9702,15.1565],[13.9332,15.1163],[13.8695,15.0428],
            [13.8622,15.0284],[13.8477,14.9959],[13.83,14.9566],[13.7965,14.8777],[13.7922,14.8023],[13.8116,14.7272],[13.7972,14.7127],[13.7885,14.704],[13.7456,14.6983],[13.7023,14.6569],
            [13.6769,14.6317],[13.6925,14.6129],[13.696,14.5511],[13.6409,14.5137],[13.5721,14.5057],[13.4934,14.4746],[13.4735,14.4428],[13.4796,14.3796],[13.501,14.2926],[13.5636,14.0142],
            [13.6345,13.7107],[13.5921,13.7107],[13.5549,13.7113],[13.4568,13.7112],[13.4162,13.7092],[13.3762,13.7104],[13.3625,13.7117],[13.3348,13.6933],[13.3148,13.6894],[13.3087,13.6812],
            [13.2995,13.6743],[13.3004,13.6642],[13.2832,13.6516],[13.2712,13.6431],[13.265,13.6311],[13.2572,13.6178],[13.2483,13.613],[13.2548,13.5969],[13.2652,13.5941],[13.2517,13.5806],
            [13.2355,13.5848],[13.2331,13.5717],[13.2414,13.5705],[13.2376,13.5583],[13.2216,13.5528],[13.2157,13.5515],[13.2083,13.5266],[13.1987,13.5188],[13.1916,13.5149],[13.1839,13.5322],
            [13.1653,13.5283],[13.163,13.5219],[13.158,13.5129],[13.1495,13.5155],[13.142,13.518],[13.1444,13.5367],[13.1482,13.5477],[13.139,13.5401],[13.1225,13.5362],[13.1253,13.5247],
            [13.123,13.5197],[13.1007,13.5308],[13.0908,13.5147],[13.0833,13.5195],[13.0671,13.5271],[13.0715,13.535],[13.0814,13.5457],[13.065,13.5471],[13.0548,13.5394],[13.0476,13.5414],
            [13.0467,13.5244],[13.0302,13.5321],[13.0262,13.531],[13.012,13.5139],[13.0045,13.5111],[12.9951,13.514],[12.9861,13.5098],[12.9741,13.5139],[12.9612,13.4972],[12.9469,13.5029],
            [12.9305,13.4934],[12.9062,13.4811],[12.8925,13.4856],[12.8771,13.4971],[12.8726,13.4881],[12.8794,13.4775],[12.8744,13.4704],[12.8585,13.48],[12.8521,13.4741],[12.8512,13.4686],
            [12.8625,13.4656],[12.8612,13.4366],[12.8417,13.4437],[12.8354,13.438],[12.838,13.429],[12.8276,13.4263],[12.8152,13.4233],[12.829,13.4198],[12.834,13.4044],[12.8279,13.3968],
            [12.8222,13.4056],[12.821,13.3966],[12.8003,13.381],[12.7942,13.375],[12.7942,13.3688],[12.7724,13.3541],[12.7548,13.352],[12.7404,13.3403],[12.7385,13.3318],[12.7421,13.3251],
            [12.7305,13.3189],[12.7139,13.3145],[12.7143,13.3042],[12.7037,13.3134],[12.6929,13.3132],[12.6939,13.3005],[12.6765,13.2743],[12.6683,13.2738],[12.6598,13.2856],[12.6509,13.2837],
            [12.647,13.3005],[12.6403,13.297],[12.6261,13.2723],[12.6094,13.2766],[12.5892,13.2778],[12.5914,13.2633],[12.5789,13.2683],[12.5746,13.2499],[12.5662,13.2374],[12.5682,13.2261],
            [12.5535,13.2191],[12.5501,13.2009],[12.5406,13.2128],[12.5368,13.2037],[12.5436,13.1924],[12.5532,13.191],[12.5652,13.1931],[12.5534,13.1761],[12.5588,13.1577],[12.5462,13.1492],
            [12.5396,13.1393],[12.537,13.1462],[12.5187,13.1499],[12.5044,13.139],[12.4908,13.1197],[12.4917,13.1018],[12.4969,13.0937],[12.4917,13.0882],[12.4969,13.0838],[12.4793,13.081],
            [12.4805,13.0647],[12.4709,13.0633],[12.4528,13.0718],[12.407,13.079],[12.4021,13.0773],[12.3688,13.0785],[12.3657,13.0897],[12.3617,13.0808],[12.3521,13.0794],[12.3408,13.0842],
            [12.3368,13.0718],[12.3347,13.083],[12.3072,13.0957],[12.2871,13.092],[12.2824,13.0837],[12.2871,13.08],[12.2749,13.0832],[12.273,13.0954],[12.2652,13.1096],[12.2412,13.1147],
            [12.2338,13.1073],[12.2185,13.114],[12.2072,13.1204],[12.1884,13.1204],[12.1786,13.1252],[12.1793,13.1153],[12.1802,13.1038],[12.1704,13.1038],[12.1577,13.1081],[12.149,13.1056],
            [12.1493,13.0969],[12.1347,13.1042],[12.1298,13.0912],[12.1141,13.0903],[12.0454,13.1298],[12.0115,13.1583],[11.9285,13.2229],[11.8846,13.2465],[11.7861,13.2685],[11.6611,13.2994],
            [11.6015,13.3191],[11.522,13.3531],[11.4801,13.3561],[11.3956,13.3701],[11.3023,13.3725],[11.181,13.3747],[11.1746,13.376],[11.0651,13.3756],[11.025,13.3724],[10.8604,13.3666],
            [10.7557,13.3602],[10.6547,13.3541],[10.5465,13.3131],[10.4664,13.2825],[10.2692,13.2706],[10.2578,13.2714],[10.0609,13.2035],[10.0333,13.1834],[9.9915,13.1565],[9.8694,13.0358],
            [9.8328,12.9961],[9.812,12.9661],[9.7904,12.9402],[9.7699,12.9175],[9.6886,12.8353],[9.6502,12.8036],[9.5807,12.8079],[9.5312,12.8096],[9.4351,12.8193],[9.3903,12.8231],
            [9.3533,12.8171],[9.3056,12.8112],[9.288,12.8121],[9.2583,12.8198],[9.2298,12.8245],[9.1789,12.8279],[9.1471,12.834],[9.1382,12.8343],[9.0812,12.835],[9.0147,12.8388],
            [8.9837,12.8391],[8.9698,12.8331],[8.8824,12.8631],[8.8606,12.8705],[8.8245,12.8808],[8.7879,12.8931],[8.7726,12.8967],[8.7258,12.9126],[8.7098,12.9136],[8.6964,12.9168],
            [8.6448,12.9461],[8.64,12.9612],[8.6018,13.0105],[8.5856,13.0242],[8.5311,13.0567],[8.4864,13.0697],[8.4217,13.0552],[8.4007,13.0702],[8.3811,13.0838],[8.3563,13.1144],
            [8.3158,13.1465],[8.2938,13.1672],[8.2559,13.2075],[8.2117,13.219],[8.1581,13.261],[8.1067,13.2893],[8.0676,13.3025],[8.037,13.3064],[8.0229,13.3111],[7.9475,13.3236],
            [7.8817,13.3296],[7.8249,13.3396],[7.8042,13.3343],[7.749,13.3021],[7.726,13.693],[7.6505,13.2412],[7.6443,13.2368],[7.6216,13.2214],[7.5846,13.2001],[7.5059,13.1558],
            [7.4741,13.1382],[7.4263,13.1105],[7.4008,13.1017],[7.3315,13.1011],[7.2279,13.1109],[7.2119,13.0933],[7.1931,13.0778],[7.1516,13.0323],[7.1247,13.0208],[7.0101,12.9915],
            [6.9466,12.9914],[6.9135,13.0057],[6.8916,13.0318],[6.792,13.1586],[6.7369,13.256],[6.6777,13.3556],[6.6361,13.3949],[6.5718,13.4584],[6.4336,13.592],[6.4147,13.6028],
            [6.3026,13.6604],[6.2689,13.6666],[6.2244,13.6664],[6.1944,13.6567],[6.1494,13.6428],[6.0848,13.68],[5.8857,13.7479],[5.7532,13.7944],[5.4593,13.8739],[5.4444,13.8699],
            [5.2705,13.7461],[5.1646,13.7446],[5.1351,13.7506],[5.106,13.7525],[5.0019,13.7412],[4.8983,13.7544],[4.8707,13.7825],[4.7423,13.7571],[4.626,13.7368],[4.5502,13.7208],
            [4.4781,13.7048],[4.3502,13.6053],[4.3207,13.5791],[4.2134,13.4853],[4.1972,13.4743],[4.173,13.4733],[4.1276,13.4503],[4.1282,13.1865],[4.1226,13.1103],[4.0961,12.9958],
            [4.0307,12.9041],[4.0036,12.8644],[3.9325,12.7559],[3.8665,12.7055],[3.8172,12.6682],[3.7223,12.5898],[3.6963,12.5664],[3.6414,12.5038],[3.6497,12.3658],[3.6552,12.2817],
            [3.6369,12.2002],[3.6349,12.1632],[3.6308,12.1172],[3.6688,11.9779],[3.6261,11.9305],[3.6177,11.9169],[3.6268,11.8394],[3.6659,11.8105],[3.6794,11.7636],[3.6051,11.697],
            [3.5683,11.719],[3.5484,11.7438],[3.5606,11.7702],[3.5419,11.7781],[3.5228,11.7878],[3.5194,11.8003],[3.5147,11.8228],[3.4939,11.8433],[3.4814,11.8614],[3.4614,11.8653],
            [3.4411,11.8769],[3.4183,11.8786],[3.403,11.8775],[3.3796,11.8867],[3.3394,11.8852],[3.3219,11.8857],[3.3021,11.8941],[3.2831,11.9342],[3.2725,11.9626]
        ]

    def get_phase(self, phase_name, num_drones, **kwargs):
        """
        Returns (positions, colors) for a given phase.
        """
        if phase_name == "phase1_pluie":
            return self._phase_1_pluie(num_drones)
        elif phase_name == "phase2_anem":
            return self._text_formation("ANEM", num_drones, self.colors["star_white"]) # Maintain White/Starry
        elif phase_name == "phase3_jcn":
            return self._text_formation("JCN2026", num_drones, self.colors["star_white"], scale_override=4.5)
        elif phase_name == "phase4_fes":
            return self._text_formation("FES-MEKNES", num_drones, self.colors["star_white"], scale_override=3.2)
        elif phase_name == "phase5_niger":
            return self._text_formation("NIGER", num_drones, self.colors["star_white"], scale_override=6.0)
        elif phase_name == "phase6_drapeau":
            # Original flag uses national colors
            return self._phase_6_drapeau(num_drones)
        elif phase_name == "phase7_carte":
            return self._phase_7_carte(num_drones)
        elif phase_name == "phase8_finale":
            return self._phase_8_finale(num_drones)
        elif phase_name == "phase9_agadez":
            return self._phase_9_agadez(num_drones)
        elif phase_name == "phase10_touareg":
            return self._phase_10_touareg(num_drones)
        elif phase_name == "act0_pre_opening":
            return self._act_0_pre_opening(num_drones)
        elif phase_name == "act1_desert":
            return self._act_1_desert(num_drones)
        elif phase_name == "act2_sacred_rain":
            return self._act_2_sacred_rain(num_drones)
        elif phase_name == "act3_typography":
            # Monolithic typography in pure starry white
            return self._text_formation("NIGER", num_drones, self.colors["star_white"], scale_override=12.0)
        elif phase_name == "act4_science":
            return self._act_4_science(num_drones)
        elif phase_name == "act5_wildlife":
            return self._act_5_wildlife(num_drones)
        elif phase_name == "act6_identity":
            # Silver/Diamond styled Agadez Cross for Sacred Identity
            return self._phase_11_croix_agadez(num_drones)
        elif phase_name == "act7_flag":
            # Immense and majestic flag
            return self._act_7_flag(num_drones)
        elif phase_name == "act8_finale":
            return self._act_8_finale(num_drones)
        elif phase_name == "miroir_celeste":
            t = kwargs.get('t', 0.0)
            return self._miroir_celeste(num_drones, t)
        elif phase_name == "phase11_croix_agadez":
            return self._phase_11_croix_agadez(num_drones)
        else:
            # Default fallback: Sphere
            return self._shape_sphere(num_drones, 50.0, self.colors["turquoise"])

    def _text_formation(self, text, num_drones, color, scale_override=None):
        # Solid Text Rendering: Every character pixel is filled with drones.
        # "Pensez peinture, pas dessin au trait."
        
        font = {
            'A': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'N': [[1,0,0,0,1],[1,1,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,1,1],[1,0,0,0,1]],
            'E': [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            'M': [[1,0,0,0,1],[1,1,0,1,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'J': [[0,0,0,0,1],[0,0,0,0,1],[0,0,0,0,1],[0,0,0,0,1],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'C': [[0,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[0,1,1,1,1]],
            '2': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,1,1,0],[0,1,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            '0': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '6': [[0,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'F': [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],
            'S': [[0,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[0,1,1,1,0],[0,0,0,0,1],[0,0,0,0,1],[1,1,1,1,0]],
            '-': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            'K': [[1,0,0,1,0],[1,0,0,1,0],[1,0,1,0,0],[1,1,0,0,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,1,0]],
            'I': [[0,1,1,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,1,0]],
            'G': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'R': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],
        }
        
        scale = scale_override if scale_override else 7.0
        char_w, char_h = 5 * scale, 7 * scale 
        spacing = 6 * scale
        
        total_w = len(text) * spacing - (spacing - char_w)
        
        def is_in_text(lx, ly):
            x_rel = lx + total_w/2
            if x_rel < 0 or x_rel > total_w: return False
            
            char_idx = int(x_rel // spacing)
            if char_idx >= len(text): return False
            
            char = text[char_idx]
            if char not in font: return False
            
            cx = x_rel % spacing
            if cx > char_w: return False 
            
            cy = char_h/2 - ly
            if cy < 0 or cy > char_h: return False
            
            grid_c = int(cx // scale)
            grid_r = int(cy // scale)
            
            if 0 <= grid_r < 7 and 0 <= grid_c < 5:
                return font[char][grid_r][grid_c] == 1
            return False

        # Use helper for solid filling
        # Lower center Y to 60 for better framing
        return self._fill_shape_uniformly(is_in_text, (-total_w/2, total_w/2, -char_h/2, char_h/2), num_drones, center=(0, 60, 0), z_depth=5.0)


    def _shape_cube(self, num, size, color):
        # Simple random cube for testing
        pos = np.random.uniform(-size/2, size/2, (num, 3))
        pos[:, 1] += 50 # Lift up
        cols = np.tile(color, (num, 1))
        return pos, cols

    def _shape_sphere(self, num, radius, color):
        # Fibonacci sphere
        indices = np.arange(0, num, dtype=float) + 0.5
        phi = np.arccos(1 - 2*indices/num)
        theta = np.pi * (1 + 5**0.5) * indices
        
        x = radius * np.cos(theta) * np.sin(phi)
        y = radius * np.sin(theta) * np.sin(phi) + 50 # Lower altitude
        z = radius * np.cos(phi)
        
        pos = np.column_stack((x, y, z))
        cols = np.tile(color, (num, 1))
        return pos, cols

    def _fill_shape_uniformly(self, inclusion_func, bounds, num_drones, center=(0, 70, 0), z_depth=1.0):
        """
        Generates a solid uniform grid of points filtered by inclusion_func.
        Every drone acts as a pixel in a dense photo.
        """
        min_x, max_x, min_y, max_y = bounds
        
        # 1. Estimate grid resolution to get ~4x more points than drones for flexibility
        area = (max_x - min_x) * (max_y - min_y)
        # We assume about 30-50% of the bounding box is filled.
        # N_total * fill_factor = num_drones * 10 
        # N_total = (num_drones * 10) / fill_factor
        grid_points_target = num_drones * 20
        res = int(np.sqrt(grid_points_target))
        
        x_grid = np.linspace(min_x, max_x, res)
        y_grid = np.linspace(min_y, max_y, res)
        
        candidates = []
        for gx in x_grid:
            for gy in y_grid:
                if inclusion_func(gx, gy):
                    candidates.append([gx, gy])
        
        candidates = np.array(candidates)
        if len(candidates) < num_drones:
            # Fallback to random if grid is too sparse (shouldn't happen with target * 20)
            return self._shape_sphere(num_drones, 20, [1,1,1]) # Emergency fallback

        # 2. Uniformly sub-sample
        # To avoid strictly repeating patterns, we can shuffle and pick
        indices = np.linspace(0, len(candidates)-1, num_drones).astype(int)
        sampled = candidates[indices]
        
        final_pos = np.zeros((num_drones, 3))
        # Center the shape
        final_pos[:, 0] = sampled[:, 0] + center[0]
        final_pos[:, 1] = sampled[:, 1] + center[1]
        final_pos[:, 2] = np.random.uniform(-z_depth/2, z_depth/2, num_drones) + center[2]
        
        final_cols = np.tile(self.colors["blanc_pure"], (num_drones, 1))
        return final_pos, final_cols

    def _act_0_pre_opening(self, num):
        # Sparse stars (Silence avant la naissance)
        pos = np.random.uniform(-150, 150, (num, 3))
        pos[:, 1] = np.random.uniform(50, 150, num) # High altitude
        cols = np.tile(self.colors["star_white"], (num, 1))
        return pos, cols

    def _act_1_desert(self, num):
        # Desert Birth (Le Désert Vivant) - Horizontal Waves
        # Expanded to fill the entire 400x400 grid (plate carrelée)
        pos = np.zeros((num, 3))
        cols = np.tile(self.colors["soleil_or"], (num, 1))
        
        # Grid dimensions to cover -200 to 200
        rows = int(np.sqrt(num))
        cols_n = num // rows
        
        grid_width = 400.0
        grid_length = 400.0
        
        dx = grid_width / (cols_n - 1)
        dz = grid_length / (rows - 1)
        
        idx = 0
        for r in range(rows):
            for c in range(cols_n):
                if idx >= num: break
                x = -200.0 + c * dx
                z = -200.0 + r * dz
                # Base Y is ground level with breathing dunes
                y = 2.0 + 4.0 * np.sin(x * 0.05) * np.cos(z * 0.05)
                pos[idx] = [x, y, z]
                
                # Bi-color mix (Gold/Orange)
                if np.random.rand() > 0.5:
                    cols[idx] = self.colors["orange_niger"]
                idx += 1
        return pos, cols

    def _act_2_sacred_rain(self, num):
        # Sacred Rain -> LE FLEUVE NIGER (The Niger River)
        pos = np.zeros((num, 3))
        cols = np.tile(self.colors["star_blue"], (num, 1))
        length = 240.0
        width_base = 25.0
        for i in range(num):
            t = (i / num) * 2.0 - 1.0 
            x = t * length / 2
            z = 45.0 * np.sin(x * 0.03) + 15.0 * np.cos(x * 0.07)
            perp_off = np.random.uniform(-width_base/2, width_base/2)
            y = 65.0 + 12.0 * np.sin(x * 0.015)
            pos[i] = [x, y, z + perp_off]
            if np.random.rand() > 0.8: cols[i] = self.colors["blanc_pure"]
        return pos, cols
        
    def _phase_1_pluie(self, num):
        # "Vagues du Niger" - Horizontal layers with central Sun
        pos = np.zeros((num, 3))
        cols = np.zeros((num, 3))
        num_layers = 5
        drones_per_layer = num // num_layers
        width, depth = 160.0, 80.0
        center_y, layer_spacing = 60.0, 12.0
        idx = 0
        for l in range(num_layers):
            layer_y = center_y + (l - num_layers/2) * layer_spacing
            for d in range(drones_per_layer):
                if idx >= num: break
                x = np.random.uniform(-width/2, width/2)
                z = np.random.uniform(-depth/2, depth/2)
                pos[idx] = [x, layer_y, z]
                sun_radius = 15.0
                if (x**2 + z**2) <= sun_radius**2:
                    cols[idx] = self.colors["orange_niger"]
                else:
                    cols[idx] = self.colors["blanc_pure"]
                idx += 1
        return pos, cols

    def _act_4_science(self, num):
        # Universal Science: Fibonacci Spiral and Sine Wave
        # Intertwined math-art
        pos = np.zeros((num, 3))
        cols = np.tile(self.colors["star_blue"], (num, 1))
        
        # Fibonacci part (Half drones)
        n_fib = num // 2
        indices = np.arange(n_fib)
        phi = (1 + np.sqrt(5)) / 2
        r = np.sqrt(indices) * 4.0
        theta = 2 * np.pi * indices / phi**2
        
        pos[:n_fib, 0] = r * np.cos(theta)
        pos[:n_fib, 1] = 80 + r * np.sin(theta) * 0.2 # Tilted spiral
        pos[:n_fib, 2] = -10 + r * np.sin(theta)
        
        # Sine Wave part (Half drones)
        n_sine = num - n_fib
        x = np.linspace(-80, 80, n_sine)
        pos[n_fib:, 0] = x
        pos[n_fib:, 1] = 70 + 20 * np.sin(x * 0.1)
        pos[n_fib:, 2] = 20 * np.cos(x * 0.1)
        
        return pos, cols

    def _act_5_wildlife(self, num):
        # African Soul (Wildlife Silhouettes)
        # Giraffe and Elephant majestic front-facing paintings
        
        def is_in_wildlife(lx, ly):
            # 🦒 GIRAFFE (Left side centered at -30)
            gx, gy = lx + 40, ly - 30
            # Body
            if (gx/10)**2 + (gy/15)**2 <= 1.0: return True
            # Neck
            if abs(gx+2) < 4 and 10 <= gy <= 50: return True
            # Head
            if (gx+4)**2 + (gy-55)**2 <= 25: return True
            # Legs
            if abs(gx-5) < 2 and -30 <= gy <= -15: return True
            if abs(gx+5) < 2 and -30 <= gy <= -15: return True
            
            # 🐘 ELEPHANT (Right side centered at 40)
            ex, ey = lx - 40, ly - 20
            # Body
            if (ex/25)**2 + (ey/18)**2 <= 1.0: return True
            # Head
            if (ex-25)**2 + (ey-5)**2 <= 100: return True
            # Trunk
            if ex > 35 and abs(ey - (- (ex-35)*0.5)) < 4 and ex < 55: return True
            # Legs
            if abs(ex-15) < 5 and -40 <= ey <= -18: return True
            if abs(ex+15) < 5 and -40 <= ey <= -18: return True
            
            return False

        return self._fill_shape_uniformly(is_in_wildlife, (-80, 80, -40, 60), num, center=(0, 60, 0), z_depth=5.0)

    def _act_7_flag(self, num):
        # Majestic Flag (Immense & Waving)
        # Larger scale than standard flag
        cols_grid = 50
        rows_grid = num // cols_grid
        
        pos = np.zeros((num, 3))
        cols = np.zeros((num, 3))
        
        width = 240.0 # Immense
        height = 135.0
        start_y = 35.0 # Lowered
        
        dx = width / (cols_grid - 1)
        dy = height / (rows_grid - 1)
        
        idx = 0
        for r in range(rows_grid):
            for c in range(cols_grid):
                if idx >= num: break
                x = c * dx - width/2
                y = (rows_grid - 1 - r) * dy + start_y
                pos[idx] = [x, y, 0]
                
                # Flag Colors
                if y > start_y + (2*height/3):
                    cols[idx] = self.colors["orange_niger"]
                elif y > start_y + (height/3):
                    # White band with Orange Sun in middle
                    sun_radius = height / 8
                    center_y = start_y + height/2
                    if (x**2 + (y - center_y)**2) <= sun_radius**2:
                        cols[idx] = self.colors["orange_niger"]
                    else:
                        cols[idx] = self.colors["blanc_pure"]
                else:
                    cols[idx] = self.colors["vert_niger"]
                idx += 1
        return pos, cols

    def _act_8_finale(self, num):
        # Unity Finale: Heart Sphere -> Star Explosion
        # We return the "Heart" as the final stop
        pos = np.zeros((num, 3))
        cols = np.tile(self.colors["blanc_pure"], (num, 1))
        
        # Fibonacci Sphere compressed into a Heart shape
        indices = np.arange(num) + 0.5
        phi = np.arccos(1 - 2*indices/num)
        theta = np.pi * (1 + 5**0.5) * indices
        
        r = 40.0
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta) + 70
        z = r * np.cos(phi)
        
        # Heart formula deformation
        # x' = x
        # y' = y + 0.3 * abs(x)
        # z' = z * 0.5
        pos[:, 0] = x
        pos[:, 1] = y + 0.3 * np.abs(x)
        pos[:, 2] = z * 0.5
        
        return pos, cols

    def _phase_3_jcn(self, num):
        # "JCN2026" - Matrix Style, Unified White
        return self._text_formation("JCN2026", num, self.colors["blanc_pure"], scale_override=4.0)

    def _phase_4_fes(self, num):
        # "FES-MEKNES" - Matrix Style, Unified White
        # Longer string -> Reduce scale further
        return self._text_formation("FES-MEKNES", num, self.colors["blanc_pure"], scale_override=3.5)

    def _phase_5_niger(self, num):
        # "NIGER" - Matrix Style, Unified White
        return self._text_formation("NIGER", num, self.colors["blanc_pure"], scale_override=5.5)

    def _phase_6_drapeau(self, num):
        # "Drapeau Flottant / Surface Vivante"
        cols_grid = 40
        rows_grid = num // cols_grid
        
        pos = np.zeros((num, 3))
        cols = np.zeros((num, 3))
        
        width = 160.0
        height = 90.0
        start_y = 25.0 # Centered lower for flag
        
        dx = width / (cols_grid - 1)
        dy = height / (rows_grid - 1)
        
        idx = 0
        for r in range(rows_grid):
            for c in range(cols_grid):
                if idx >= num: break
                x = c * dx - width/2
                y = (rows_grid - 1 - r) * dy + start_y
                pos[idx] = [x, y, 0]
                
                # Flag Colors
                if y > start_y + (2*height/3):
                    cols[idx] = self.colors["orange_niger"]
                elif y > start_y + (height/3):
                    # White band with Orange Sun
                    sun_radius = height / 8
                    center_y = start_y + height/2
                    if (x**2 + (y - center_y)**2) <= sun_radius**2:
                        cols[idx] = self.colors["orange_niger"]
                    else:
                        cols[idx] = self.colors["blanc_pure"]
                else:
                    cols[idx] = self.colors["vert_niger"]
                idx += 1
        return pos, cols

    def _phase_7_carte(self, num):
        # Precise Niger Map - Pure Solid Surface Rendering
        poly = np.array(self.niger_coords)
        min_lon, min_lat = np.min(poly, axis=0)
        max_lon, max_lat = np.max(poly, axis=0)
        
        target_width = 140.0
        scale = target_width / (max_lon - min_lon)
        
        # Define local bounds for the helper
        l_min_x = (min_lon - (min_lon + max_lon)/2) * scale
        l_max_x = (max_lon - (min_lon + max_lon)/2) * scale
        l_min_y = (min_lat - (min_lat + max_lat)/2) * scale
        l_max_y = (max_lat - (min_lat + max_lat)/2) * scale
        
        return self._fill_shape_uniformly(is_in_niger, (l_min_x, l_max_x, l_min_y, l_max_y), num, center=(0, 55, 0))

    def _is_inside_polygon(self, x, y, poly):
        # Ray casting algorithm
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside


    def _phase_8_finale(self, num):
        # Spectacular Finale: 8-branch star 3D
        pos = np.zeros((num, 3))
        cols = np.tile(self.colors["blanc_pure"], (num, 1))
        
        # Fibonacci sphere for the core
        core_num = num // 2
        indices = np.arange(0, core_num, dtype=float) + 0.5
        phi = np.arccos(1 - 2*indices/core_num)
        theta = np.pi * (1 + 5**0.5) * indices
        radius = 25.0
        pos[:core_num, 0] = radius * np.cos(theta) * np.sin(phi)
        pos[:core_num, 1] = radius * np.sin(theta) * np.sin(phi) + 70
        pos[:core_num, 2] = radius * np.cos(phi)
        
        # Rays
        rays_num = num - core_num
        rays = 8
        drones_per_ray = rays_num // rays
        for r in range(rays):
            angle = (2 * np.pi / rays) * r
            for d in range(drones_per_ray):
                idx = core_num + r * drones_per_ray + d
                dist = radius + d * 2.5
                pos[idx] = [
                    dist * np.cos(angle),
                    dist * np.sin(angle) + 70,
                    np.random.uniform(-3, 3)
                ]
        return pos, cols

    def _phase_9_agadez(self, num):
        # "La Grande Mosquée d'Agadez" - Solid Image Rendering
        # Front-facing silhouette with tapering tower and torons
        
        def is_in_mosque(lx, ly):
            # 1. Main Tower (Tapering)
            # Base width 34, Top width 8, Height 90, starts at Y=20
            h = ly - 20
            if 0 <= h <= 90:
                w_curr = 34.0 * (1 - h/90.0) + 8.0 * (h/90.0)
                if abs(lx) <= w_curr / 2: return True
                
                # 2. Torons (Beams)
                # Every 8 meters vertically
                if abs(h % 8 - 4) < 1.0: # Horizontal bars
                    if abs(lx) <= w_curr / 2 + 5.0: return True
            
            # 3. Base Building
            if (0 <= ly <= 20) and (-50 <= lx <= 50): return True
            
            return False

        pos, cols = self._fill_shape_uniformly(is_in_mosque, (-60, 60, 0, 110), num, center=(0, 20, 0), z_depth=5.0)
        # Apply Miroir Céleste Colors (Gold/Orange mix)
        cols = np.tile(self.colors["soleil_or"], (num, 1))
        # Random mix with orange for a "living" building look
        orange_indices = np.random.rand(num) > 0.8
        cols[orange_indices] = self.colors["orange_niger"]
        return pos, cols

    def _phase_10_touareg(self, num):
        # "Touareg avec son chameau" - Solid Image Rendering
        # Narrative silhouette
        
        def is_in_scene(lx, ly):
            # --- CAMEL ---
            # Body
            bx, by = lx - 15, ly - 30
            if (bx/15)**2 + (by/10)**2 <= 1.0: return True
            # Hump
            hx, hy = lx - 15, ly - 42
            if (hx/7)**2 + (hy/5)**2 <= 1.0: return True
            # Neck & Head
            nx, ny = lx - 2, ly - 35
            if (lx < 0) and abs(ny - (-lx * 0.8)) < 4.0 and lx > -20: return True
            
            # --- TOUAREG ---
            # Standing next to camel
            tx, ty = lx + 25, ly - 20
            if (abs(tx) <= 6) and (0 <= ly <= 40): return True
            # Head/Turban
            thx, thy = lx + 25, ly - 45
            if thx**2 + thy**2 <= 25: return True
            
            return False

        return self._fill_shape_uniformly(is_in_scene, (-40, 50, 0, 60), num, center=(0, 25, 0), z_depth=3.0)

    def _phase_11_croix_agadez(self, num):
        # "Croix d'Agadez" - Solid Image Rendering
        # Composite inclusion function for the sacred symbol
        
        # Parameters (matching previous geometric design but for grid fill)
        sc = 0.85 # Scale factor to "diminue la taille un peu"
        inner_r, outer_r = 8.0 * sc, 16.0 * sc
        arm_w, arm_h = 12.0 * sc, 8.0 * sc
        arm_off_x, arm_off_y = 22.0 * sc, -10.0 * sc
        angle_rad = np.radians(20)
        d_size = 10.0 * sc
        t_size = 6.0 * sc
        
        def is_in_croix(lx, ly):
            # 1. Ring
            dist = np.sqrt(lx**2 + ly**2)
            if inner_r <= dist <= outer_r: return True
            
            # 2. Lateral Arms
            def in_arm(px, py, flip=False):
                # Back rotate
                ang = -angle_rad if not flip else angle_rad
                rx = px * np.cos(ang) + py * np.sin(ang)
                ry = -px * np.sin(ang) + py * np.cos(ang)
                return (-arm_w/2 <= rx <= arm_w/2) and (-arm_h/2 <= ry <= arm_h/2)
            
            if in_arm(lx - arm_off_x, ly - arm_off_y): return True
            if in_arm(lx + arm_off_x, ly - arm_off_y, True): return True
            
            # 3. Upper Part (Diamond Head + Neck)
            # Neck
            if (-3 <= lx <= 3) and (outer_r <= ly <= outer_r + 12): return True
            # Head
            dy = ly - (outer_r + 20)
            if (abs(lx) + abs(dy) <= d_size): return True
            
            # 4. Lower Part (Tapering Body + Terminal)
            if ((-16 - 40)*sc <= ly <= -outer_r): # Body range
                h_rel = (ly + outer_r) / (-40.0 * sc)
                if 0 <= h_rel <= 1:
                    w_curr = 12.0 * sc * (1 - h_rel) + 4.0 * sc * h_rel
                    if abs(lx) <= w_curr / 2: return True
            # Terminal
            ty = ly - ((-16 - 40 - 8) * sc)
            if (abs(lx) + abs(ty) <= t_size): return True
            
            return False

        # center_z = -30.0 Move it "un peu derriere"
        return self._fill_shape_uniformly(is_in_croix, (-35*sc, 35*sc, -70*sc, 45*sc), num, center=(0, 75, -30.0))

    def _miroir_celeste(self, num, t):
        # Miroir Céleste Show (45s total)
        pos = np.zeros((num, 3))
        cols = np.tile(self.colors["blanc_pure"], (num, 1))
        
        def get_base_mosque(n):
            p = np.zeros((n, 3))
            c = np.tile(self.colors["soleil_or"], (n, 1))
            for i in range(n):
                if i < n * 0.4: # Base building
                    p[i] = [np.random.uniform(-50, 50), np.random.uniform(0, 20), np.random.uniform(-5, 5)]
                else: # Main Tower
                    h = np.random.uniform(0, 90)
                    w = 34.0 * (1 - h/90.0) + 8.0 * (h/90.0)
                    p[i] = [np.random.uniform(-w/2, w/2), 20 + h, np.random.uniform(-w/2, w/2)]
            return p, c

        # --- Sub-Phases ---
        if t <= 10.0: # CONNECTION (Extension)
            p, c = get_base_mosque(num)
            prog = t / 10.0
            n_ext = int(num * prog * 0.4)
            for i in range(n_ext):
                eh = (i / n_ext) * 80.0 * prog
                w = 8.0 * (1 - eh/80.0)
                p[i] = [np.random.uniform(-w/2, w/2), 110 + eh, np.random.uniform(-w/2, w/2)]
                mix = i / n_ext
                c[i] = np.array(self.colors["soleil_or"]) * (1-mix) + np.array(self.colors["star_white"]) * mix
            return p, c
        elif t <= 25.0: # DISSOLUTION (Particles)
            p, c = get_base_mosque(num)
            prog = (t - 10.0) / 15.0
            for i in range(num):
                lp = max(0, prog - (p[i, 1] / 150.0) * 0.5)
                ang = lp * 12 * np.pi + i * 0.1
                r = 10 + lp * 60
                p[i, 0] += r * np.cos(ang)
                p[i, 2] += r * np.sin(ang)
                p[i, 1] += lp * 120
                c[i] = np.array(self.colors["soleil_or"]) * (1-lp) + np.array(self.colors["star_blue"]) * lp
            return p, c
        elif t <= 35.0: # MIRROR (Inverted)
            p, c = get_base_mosque(num)
            prog = (t - 25.0) / 10.0
            my = 110.0
            for i in range(num):
                y_ref = 2 * my - p[i, 1]
                p[i, 1] = p[i, 1] * (1-prog) + y_ref * prog
                c[i] = np.array(self.colors["soleil_or"]) * (1-prog) + np.array(self.colors["star_blue"]) * prog
            return p, c
        else: # ASCENSION (The Starry Night)
            p, c = get_base_mosque(num)
            prog = min(1.0, (t-35.0)/10.0)
            for i in range(num):
                p[i, 1] += prog * 180
                p[i, 2] += np.random.uniform(-50, 50) * prog
                p[i, 0] += np.random.uniform(-50, 50) * prog
                c[i] = np.array(self.colors["star_white"]) * (1-prog)
            return p, c
