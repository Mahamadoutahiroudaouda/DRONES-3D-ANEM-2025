import numpy as np
from PIL import Image
import os

class FormationLibrary:
    def __init__(self):
        # === AUDIO REACTIVITY STATE ===
        self.audio_bpm = 120.0  # Placeholder: Would come from audio analysis
        self.audio_energy = 0.5  # Normalized [0, 1], from FFT analysis
        self.kick_detected = False  # Per-frame kick detection
        
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
        
        # Cache for static formations
        self._cache = {}
        self._phase10_cache = {}

    def get_phase(self, phase_name, num_drones, **kwargs):
        """
        Returns (positions, colors) for a given phase.
        Supports audio_energy for music-reactive phases.
        """
        # Extract audio_energy if provided (default 0.5)
        audio_energy = kwargs.pop('audio_energy', 0.5)
        self.audio_energy = audio_energy
        
        # Check cache for static phases (no 't' in kwargs)
        if 't' not in kwargs:
            cache_key = (phase_name, num_drones)
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        result = self._generate_phase(phase_name, num_drones, **kwargs)
        
        if 't' not in kwargs:
            self._cache[(phase_name, num_drones)] = result
            
        return result
    
    # Alias pour le chorégraphe professionnel
    def generate_formation(self, phase_name, num_drones, **kwargs):
        """Alias de get_phase pour compatibilité avec le chorégraphe."""
        return self.get_phase(phase_name, num_drones, **kwargs)

    def _generate_phase(self, phase_name, num_drones, **kwargs):
        if phase_name == "phase1_pluie":
            t = kwargs.get('t', 0.0)
            audio_energy = kwargs.get('audio_energy', self.audio_energy)
            return self._phase_1_pluie(num_drones, t, audio_energy)
        elif phase_name == "phase2_anem":
            t = kwargs.get('t', 0.0)
            return self._text_formation("ANEM", num_drones, self.colors["star_white"], effect="rotate_ring", t=t) 
        elif phase_name == "phase3_jcn":
            t = kwargs.get('t', 0.0)
            return self._text_formation("JCN2026", num_drones, self.colors["soleil_or"], scale_override=5.5, effect="wave", t=t)
        elif phase_name == "phase4_fes":
            t = kwargs.get('t', 0.0)
            return self._text_formation("FES-MEKNES", num_drones, self.colors["vert_niger"], scale_override=5.0, effect="split_move", t=t)
        elif phase_name == "phase5_niger":
            t = kwargs.get('t', 0.0)
            return self._text_formation("NIGER", num_drones, self.colors["orange_niger"], scale_override=8.5, effect="heartbeat", t=t)
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
            t = kwargs.get('t', 0.0)
            return self._phase_10_touareg(num_drones, t)
        elif phase_name == "dubai_camel":
            t = kwargs.get('t', 0.0)
            return self._phase_dubai_camel(num_drones, t)
        elif phase_name == "act0_pre_opening":
            t = kwargs.get('t', 0.0)
            return self._act_0_pre_opening(num_drones, t)
        elif phase_name == "act1_desert":
            t = kwargs.get('t', 0.0)
            return self._act_1_desert(num_drones, t)
        elif phase_name == "act2_desert_seveille":
            t = kwargs.get('t', 0.0)
            return self._act_2_desert_seveille(num_drones, t)
        elif phase_name == "act2_sacred_rain":
            # Redirige vers le nouveau nom
            return self._act_3_fleuve_niger(num_drones)
        elif phase_name == "act3_fleuve_niger":
            return self._act_3_fleuve_niger(num_drones)
        elif phase_name == "act3_typography":
            # Monolithic typography in pure starry white
            return self._text_formation("NIGER", num_drones, self.colors["star_white"], scale_override=16.0)
        elif phase_name == "phase_touareg_spiral":
            t = kwargs.get('t', 0.0)
            audio_energy = kwargs.get('audio_energy', self.audio_energy)
            return self._phase_touareg_spiral(num_drones, t, audio_energy)
        elif phase_name == "phase_22eme_edition":
            t = kwargs.get('t', 0.0)
            audio_energy = kwargs.get('audio_energy', self.audio_energy)
            return self._phase_22eme_edition(num_drones, t, audio_energy)
        elif phase_name == "act4_science":
            t = kwargs.get('t', 0.0)
            audio_energy = kwargs.get('audio_energy', self.audio_energy)
            return self._act_4_science(num_drones, t, audio_energy)
        elif phase_name == "act5_wildlife":
            return self._act_5_wildlife(num_drones)
        elif phase_name == "act5_tree_of_life":
            t = kwargs.get('t', 0.0)
            audio_energy = kwargs.get('audio_energy', self.audio_energy)
            return self._act_5_tree_of_life(num_drones, t, audio_energy)
        elif phase_name == "act5_african_soul":
            t = kwargs.get('t', 0.0)
            audio_energy = kwargs.get('audio_energy', self.audio_energy)
            return self._act_5_african_soul(num_drones, t, audio_energy)
        elif phase_name == "act6_identity":
            # Silver/Diamond styled Agadez Cross for Sacred Identity
            return self._phase_11_croix_agadez(num_drones)
        elif phase_name == "act7_flag":
            # Immense and majestic flag
            return self._act_7_flag(num_drones)
        elif phase_name == "act8_finale":
            t = kwargs.get('t', 0.0)
            return self._act_8_finale(num_drones, t)
        elif phase_name == "act9_eagle":
            t = kwargs.get('t', 0.0)
            return self._act_9_eagle(num_drones, t)
        elif phase_name == "miroir_celeste":
            t = kwargs.get('t', 0.0)
            return self._act_finale_cosmic(num_drones, t)
        elif phase_name == "phase11_croix_agadez":
            return self._phase_11_croix_agadez(num_drones)
        else:
            # Default fallback: Sphere
            return self._shape_sphere(num_drones, 50.0, self.colors["turquoise"])

    def _text_formation(self, text, num_drones, color, scale_override=None, effect=None, t=0.0):
        # Solid Text Rendering: Every character pixel is filled with drones.
        
        scale = scale_override if scale_override else 9.0
        
        # --- CACHING OPTIMIZATION ---
        cache_key = f"TEXT_{text}_{num_drones}_{scale}"
        pos = None
        
        if cache_key in self._cache:
            pos_cached, _ = self._cache[cache_key]
            pos = pos_cached.copy()
            
        if pos is None:
            # Generate static shape if not in cache
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
            # Transform text into a luminous sculpture with significant depth (10m)
            pos, cols = self._fill_shape_uniformly(is_in_text, (-total_w/2, total_w/2, -char_h/2, char_h/2), num_drones, center=(0, 60, 0), z_depth=10.0)
            
            # Save to cache
            self._cache[cache_key] = (pos, cols)
            pos = pos.copy()

        # Override color base if needed (re-tile for every frame to ensure correct initial state before effects)
        cols = np.tile(color, (num_drones, 1))

        # --- DYNAMIC EFFECTS (LATEST GEN) ---
        if effect == "rotate_ring":
            # Slow rotation around Y
            theta = t * 0.3
            c, s = np.cos(theta), np.sin(theta)
            x, z = pos[:, 0].copy(), pos[:, 2].copy()  # Relative to origin (0,0,0) ? No, center is (0,60,0)
            
            # Recenter for rotation
            cx, cz = 0, 0 # The text is centered on x=0, z=0
            
            # Apply rotation
            pos[:, 0] = x * c + z * s
            pos[:, 2] = -x * s + z * c
            
            # Dynamic Pulse on Color
            pulse = 0.5 + 0.5 * np.sin(t * 2.0)
            cols[:, 0] = np.clip(cols[:, 0] + pulse * 0.2, 0, 1) # Add redness

        elif effect == "wave":
            # Sine wave flowing through text
            wave_amp = 5.0
            freq = 0.1
            speed = 3.0
            pos[:, 2] += wave_amp * np.sin(pos[:, 0] * freq + t * speed)
            
            # Color gradient shifting
            shift = (np.sin(t) + 1) / 2
            cols[:, 1] = shift # Shift green channel

        elif effect == "split_move":
            # FES - MEKNES split
            # Move apart and back
            offset = 15.0 * np.sin(t * 0.5) 
            mask_left = pos[:, 0] < 0
            pos[mask_left, 0] -= max(0, offset)
            pos[~mask_left, 0] += max(0, offset)
            
            # Sparkle
            if int(t * 10) % 2 == 0:
                noise = np.random.uniform(-0.1, 0.1, (num_drones, 3))
                cols = np.clip(cols + noise, 0, 1)

        elif effect == "heartbeat":
            # Violent scale pulses
            beat = np.exp(-10 * (t % 1.0)) # Sharp spikes per second
            if (t % 1.0) > 0.8: beat = 0 # rest
            
            scale = 1.0 + 0.05 * np.sin(t * 2.0) + 0.1 * beat
            
            # Scale from geometric center (0, 60, 0)
            pos[:, 0] *= scale
            pos[:, 1] = (pos[:, 1] - 60) * scale + 60
            pos[:, 2] *= scale
            
            # Strobe effect on beat
            if beat > 0.5:
                cols[:] = [1, 1, 1] # Flash white

        return pos, cols


    def _act_finale_cosmic(self, num_drones, t):
        """
        The Ultimate Cosmic Finale: Spiral -> Implosion -> Eye -> Silence.
        """
        pos = np.zeros((num_drones, 3))
        cols = np.ones((num_drones, 3))
        
        # Timeline
        # 0-10s: Spiral Galaxy Formation
        # 10-15s: Implosion to Singularity (Black Hole)
        # 15-20s: Big Bang / Eye Opening
        # 20s+: Drift to Silence
        
        if t < 10.0:
            # GALAXY SPIRAL
            progress = t / 10.0
            # Fibonacci spiral but flat and rotating
            indices = np.arange(0, num_drones, dtype=float)
            golden_angle = np.pi * (3 - np.sqrt(5))
            theta = indices * golden_angle + (t * 2.0) # Rotating
            
            # Radius expands
            max_radius = 150.0 * np.sqrt(progress)
            radius = np.sqrt(indices / num_drones) * max_radius
            
            x = radius * np.cos(theta)
            z = radius * np.sin(theta)
            
            # Height variation (Galaxy bulge)
            y_bulge = 100.0 + 30.0 * np.exp(-radius * 0.05)
            y = y_bulge
            
            pos = np.column_stack((x, y, z))
            
            # Colors: Core Gold -> Edge Blue
            dist_norm = radius / 150.0
            cols[:, 0] = 1.0 - dist_norm # Red
            cols[:, 1] = 0.8 - dist_norm * 0.5 # Green
            cols[:, 2] = dist_norm + 0.2 # Blue
            
        elif t < 14.0:
            # IMPLOSION
            # Interpolate from Galaxy to pure point at (0, 150, 0)
            progress = (t - 10.0) / 4.0
            # Ease in cubic
            progress = progress * progress * progress
            
            # Recompute spiral state at t=10
            indices = np.arange(0, num_drones, dtype=float)
            golden_angle = np.pi * (3 - np.sqrt(5))
            theta = indices * golden_angle + (20.0)
            radius = np.sqrt(indices / num_drones) * 150.0
            x = radius * np.cos(theta)
            z = radius * np.sin(theta)
            y = 100.0 + 30.0 * np.exp(-radius * 0.05)
            start_pos = np.column_stack((x, y, z))
            target_pos = np.array([0, 120, 0])
            
            pos = start_pos * (1.0 - progress) + target_pos * progress
            
            # Colors turn to pure white energy
            cols[:] = [1.0, 1.0, 1.0]

        elif t < 20.0:
            # THE COSMIC EYE / HOLLOW SPHERE
            progress = (t - 14.0) / 6.0
            # Rapid expansion to sphere
            expand_radius = 60.0 * (1.0 - np.exp(-progress * 5.0))
            
            # Sphere positions
            indices = np.arange(0, num_drones, dtype=float) + 0.5
            phi = np.arccos(1 - 2*indices/num_drones)
            theta = np.pi * (1 + 5**0.5) * indices
            
            sx = np.cos(theta) * np.sin(phi)
            sy = np.sin(theta) * np.sin(phi)
            sz = np.cos(phi)
            
            # Flatten front to look like an pupil (Irish)
            # z > 0 is front
            
            pos[:, 0] = sx * expand_radius
            pos[:, 1] = sy * expand_radius + 120.0
            pos[:, 2] = sz * expand_radius
            
            # Eye Colors
            # Center (Pupil) -> Black/Void
            # Iris -> Blue/Gold
            # Sclera -> White
            
            # Determine angle from front vector (0,0,1)
            # dot product with (0,0,1) is basically sz
            
            # Pupil: sz > 0.9
            # Iris: 0.6 < sz < 0.9
            # White: sz < 0.6
            
            is_pupil = sz > 0.85
            is_iris = (sz > 0.6) & (sz <= 0.85)
            
            cols[~is_pupil & ~is_iris] = [0.1, 0.1, 0.1] # Fading out back
            cols[is_iris] = [0.0, 0.8, 1.0] # Blue/Cyan Iris
            cols[is_pupil] = [0.0, 0.0, 0.0] # BLACK PUPIL (Negative Space)
            
            # Add rotation
            rot_speed = t * 0.5
            # Rotate around Y ...
            
        else:
             # SILENCE / DRIFT AWAY
             # Just float upwards and fade
             pos, _ = self._shape_sphere(num_drones, 60.0, [0,0,0])
             pos[:, 1] = 120.0 + (t - 20.0) * 5.0 # Float up
             cols[:] = [0,0,0] # Invisible

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

    def _fill_shape_uniformly(self, inclusion_func, bounds, num_drones, center=(0, 70, 0), z_depth=8.0):
        """
        Generates a solid uniform grid of points filtered by inclusion_func.
        Every drone acts as a pixel in a dense photo.
        Sculptural default: z_depth = 8.0 for visibility in oblique camera.
        """
        min_x, max_x, min_y, max_y = bounds
        
        # 1. Estimate grid resolution to get ~4x more points than drones for flexibility
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
            return self._shape_sphere(num_drones, 20, [1,1,1]) # Emergency fallback

        indices = np.linspace(0, len(candidates)-1, num_drones).astype(int)
        sampled = candidates[indices]
        
        final_pos = np.zeros((num_drones, 3))
        jitter = 1.0 # Subtle spread to avoid grid-like look
        final_pos[:, 0] = sampled[:, 0] + center[0] + np.random.uniform(-jitter, jitter, num_drones)
        final_pos[:, 1] = sampled[:, 1] + center[1] + np.random.uniform(-jitter, jitter, num_drones)
        final_pos[:, 2] = np.random.uniform(-z_depth/2, z_depth/2, num_drones) + center[2]
        
        final_cols = np.tile(self.colors["blanc_pure"], (num_drones, 1))
        return final_pos, final_cols

    def _sample_from_image(self, image_path, num_drones, target_width=160.0):
        """Extracts shape and colors from an image file."""
        if not os.path.exists(image_path):
            print(f"Warning: Image {image_path} not found.")
            return None, None

        img = Image.open(image_path).convert("RGBA")
        data = np.array(img)
        
        # Silhouette: find all non-transparent pixels (Alpha > 128)
        # Note: We also exclude very white/background pixels if needed, 
        # but here we rely on the alpha channel.
        mask = data[:, :, 3] > 128
        y_indices, x_indices = np.where(mask)
        
        if len(x_indices) == 0:
            return None, None
            
        # Get coordinates and colors
        coords = np.column_stack((x_indices, y_indices))
        colors = data[y_indices, x_indices, :3] / 255.0
        
        # Sub-sample to num_drones
        indices = np.linspace(0, len(coords)-1, num_drones).astype(int)
        sampled_coords = coords[indices]
        sampled_colors = colors[indices]
        
        # Center and scale
        min_x, min_y = np.min(sampled_coords, axis=0)
        max_x, max_y = np.max(sampled_coords, axis=0)
        
        width = max_x - min_x
        height = max_y - min_y
        scale = target_width / width
        
        pos = np.zeros((num_drones, 3))
        # Flip Y because image coordinates start from top
        pos[:, 0] = (sampled_coords[:, 0] - (min_x + max_x)/2) * scale
        pos[:, 1] = -(sampled_coords[:, 1] - (min_y + max_y)/2) * scale
        
        return pos, sampled_colors

    def _act_0_pre_opening(self, num, t=0.0):
        """
        🎭 ACTE 0 : LE CIEL S'ÉVEILLE - Vision Réaliste
        
        Philosophie "CIEL RÉALISTE" :
        - Horizon = 0m (niveau yeux spectateur)
        - Sol suggéré = -20m à 0m
        - Ciel des drones = 15m à 100m (zone d'action)
        - Aucun drone ne passe en dessous de y=15m
        
        TIMELINE (20s total):
        - PHASE 1 (0-3s)   : ÉTOILES NAISSANTES (20-40m) - Juste au-dessus des arbres
        - PHASE 2 (3-8s)   : ANEM LUMINEUX (30m) - Texte visible et grand
        - PHASE 3 (8-12s)  : ORBE SOLAIRE (60m) - Sphère dorée à hauteur raisonnable
        - PHASE 4 (12-20s) : ARC-EN-CIEL TERRESTRE (15-45m) - Comme un pont au-dessus du public
        
        Args:
            num: Nombre de drones (1000)
            t: Temps écoulé depuis le début de l'acte
            
        Returns:
            (positions, colors) - Arrays numpy pour les 1000 drones
        """
        rng = np.random.default_rng(2025)
        
        # ═══════════════════════════════════════════════════════════════
        # PARAMÈTRES DE CONFIGURATION - ALTITUDES RÉALISTES
        # ═══════════════════════════════════════════════════════════════
        
        # Timing des phases (en secondes)
        PHASE_1_END = 3.0      # Nuit primordiale
        PHASE_2_END = 8.0      # Constellation ANEM
        PHASE_3_END = 12.0     # Cœur cosmique
        PHASE_4_END = 20.0     # Éclosion finale
        
        # NOUVELLES ALTITUDES RÉALISTES
        ALTITUDE_ETOILES = 30.0      # Phase 1: 20-40m (moyenne 30m)
        ALTITUDE_TEXTE = 35.0        # Phase 2: Texte ANEM à 35m
        ALTITUDE_SPHERE = 60.0       # Phase 3: Sphère à 60m
        ALTITUDE_ARC_BASE = 20.0     # Phase 4: Arc-en-ciel 20-50m
        ALTITUDE_ARC_MAX = 50.0
        
        # Niveau minimum absolu (au-dessus du sol/eau)
        GROUND_CLEARANCE = 15.0
        
        # Couleurs principales
        BLEU_NUIT = np.array([0.0, 0.12, 0.25])
        BLANC = np.array([1.0, 1.0, 1.0])
        ORANGE_NIGER = np.array([1.0, 0.5, 0.0])
        VERT_NIGER = np.array([0.0, 0.6, 0.2])
        OR_SOLEIL = np.array([1.0, 0.84, 0.0])
        
        # Arc-en-ciel (7 couleurs)
        RAINBOW_COLORS = np.array([
            [0.58, 0.0, 0.83],   # Violet
            [0.29, 0.0, 0.51],   # Indigo
            [0.0, 0.0, 1.0],     # Bleu
            [0.0, 1.0, 0.0],     # Vert
            [1.0, 1.0, 0.0],     # Jaune
            [1.0, 0.65, 0.0],    # Orange
            [1.0, 0.0, 0.0],     # Rouge
        ])
        
        # ═══════════════════════════════════════════════════════════════
        # DÉTERMINATION DE LA PHASE COURANTE
        # ═══════════════════════════════════════════════════════════════
        
        if t < PHASE_1_END:
            current_phase = "NUIT_PRIMORDIALE"
            phase_progress = t / PHASE_1_END
        elif t < PHASE_2_END:
            current_phase = "CONSTELLATION_ANEM"
            phase_progress = (t - PHASE_1_END) / (PHASE_2_END - PHASE_1_END)
        elif t < PHASE_3_END:
            current_phase = "COEUR_COSMIQUE"
            phase_progress = (t - PHASE_2_END) / (PHASE_3_END - PHASE_2_END)
        else:
            current_phase = "ECLOSION_FINALE"
            phase_progress = min(1.0, (t - PHASE_3_END) / (PHASE_4_END - PHASE_3_END))
        
        # Initialisation des arrays
        pos = np.zeros((num, 3))
        cols = np.zeros((num, 3))
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 1 : ÉTOILES NAISSANTES (0-3s) - Altitude 20-40m
        # "Juste au-dessus des arbres, comme si le ciel s'allumait"
        # ═══════════════════════════════════════════════════════════════
        
        if current_phase == "NUIT_PRIMORDIALE":
            # Nombre d'étoiles visibles (progression exponentielle)
            visible_stars = int(min(100, 1 + t * t * 11))
            
            # Positions dans un dôme bas (20-40m de hauteur)
            # Distribution horizontale large, verticale limitée
            phi = rng.uniform(0, 2 * np.pi, num)
            r_horizontal = rng.uniform(20, 120, num)  # Rayon horizontal large
            
            pos[:, 0] = r_horizontal * np.cos(phi)
            pos[:, 1] = rng.uniform(20, 40, num)  # ALTITUDE BASSE : 20-40m
            pos[:, 2] = r_horizontal * np.sin(phi)
            
            # Couleurs: étoiles blanches scintillantes sur fond nuit
            cols[:, :] = BLEU_NUIT * 0.3  # Base très sombre
            
            # Seuls les premiers 'visible_stars' drones sont visibles
            visible_mask = np.arange(num) < visible_stars
            
            # Effet scintillement
            twinkle = 0.7 + 0.3 * np.sin(t * 5.0 + np.arange(num) * 0.5)
            cols[visible_mask] = BLANC * twinkle[visible_mask, None]
            
            # Première étoile plus brillante
            if visible_stars >= 1:
                cols[0] = BLANC * 1.5
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 2 : ANEM LUMINEUX (3-8s) - Altitude 35m, PLUS GRAND
        # "Texte géant visible depuis le sol, comme un néon dans le ciel"
        # ═══════════════════════════════════════════════════════════════
        
        elif current_phase == "CONSTELLATION_ANEM":
            local_t = t - PHASE_1_END
            
            # Timing des lettres
            LETTER_A_START = 0.0
            LETTER_N_START = 1.0
            LETTER_E_START = 2.0
            LETTER_M_START = 3.0
            
            # Nombre de drones par lettre
            DRONES_PER_LETTER = 200
            
            # DIMENSIONS PLUS GRANDES pour visibilité depuis le sol
            text_width = 120.0      # 120m de large (comme un terrain de foot)
            text_height = 50.0      # 50m de haut
            letter_spacing = 15.0
            letter_width = 22.0     # Lettres plus larges
            base_y = ALTITUDE_TEXTE  # 35m d'altitude
            
            # Fonctions de création des lettres (mêmes formes, nouvelle altitude)
            def create_letter_A(n_points, x_offset):
                pts = np.zeros((n_points, 3))
                for i in range(n_points):
                    t_param = i / n_points
                    if t_param < 0.4:
                        pts[i] = [x_offset - letter_width/2 + t_param * letter_width * 1.25, 
                                  base_y + t_param * 2.5 * text_height, 0]
                    elif t_param < 0.5:
                        pts[i] = [x_offset - letter_width/4 + (t_param - 0.4) * letter_width * 2.5, 
                                  base_y + text_height * 0.5, 0]
                    else:
                        pts[i] = [x_offset + letter_width/2 - (t_param - 0.5) * letter_width * 1.25, 
                                  base_y + (t_param - 0.5) * 2 * text_height, 0]
                return pts
            
            def create_letter_N(n_points, x_offset):
                pts = np.zeros((n_points, 3))
                for i in range(n_points):
                    t_param = i / n_points
                    if t_param < 0.33:
                        pts[i] = [x_offset - letter_width/2, base_y + t_param * 3 * text_height, 0]
                    elif t_param < 0.66:
                        pts[i] = [x_offset - letter_width/2 + (t_param - 0.33) * 3 * letter_width,
                                  base_y + text_height - (t_param - 0.33) * 3 * text_height, 0]
                    else:
                        pts[i] = [x_offset + letter_width/2, base_y + (t_param - 0.66) * 3 * text_height, 0]
                return pts
            
            def create_letter_E(n_points, x_offset):
                pts = np.zeros((n_points, 3))
                for i in range(n_points):
                    t_param = i / n_points
                    if t_param < 0.25:
                        pts[i] = [x_offset - letter_width/2 + t_param * 4 * letter_width, base_y + text_height, 0]
                    elif t_param < 0.5:
                        pts[i] = [x_offset - letter_width/2, base_y + text_height - (t_param - 0.25) * 4 * text_height, 0]
                    elif t_param < 0.75:
                        pts[i] = [x_offset - letter_width/2 + (t_param - 0.5) * 3 * letter_width, base_y + text_height * 0.5, 0]
                    else:
                        pts[i] = [x_offset - letter_width/2 + (t_param - 0.75) * 4 * letter_width, base_y, 0]
                return pts
            
            def create_letter_M(n_points, x_offset):
                pts = np.zeros((n_points, 3))
                for i in range(n_points):
                    t_param = i / n_points
                    if t_param < 0.25:
                        pts[i] = [x_offset - letter_width/2, base_y + t_param * 4 * text_height, 0]
                    elif t_param < 0.5:
                        pts[i] = [x_offset - letter_width/2 + (t_param - 0.25) * 2 * letter_width,
                                  base_y + text_height - (t_param - 0.25) * 2 * text_height, 0]
                    elif t_param < 0.75:
                        pts[i] = [x_offset + (t_param - 0.5) * 2 * letter_width,
                                  base_y + text_height * 0.5 + (t_param - 0.5) * 2 * text_height, 0]
                    else:
                        pts[i] = [x_offset + letter_width/2, base_y + text_height - (t_param - 0.75) * 4 * text_height, 0]
                return pts
            
            # Positions X des lettres (bien espacées)
            letter_positions = [-52, -17, 17, 52]  # 4 lettres centrées
            
            # Créer les positions pour chaque lettre
            letter_A_pos = create_letter_A(DRONES_PER_LETTER, letter_positions[0])
            letter_N_pos = create_letter_N(DRONES_PER_LETTER, letter_positions[1])
            letter_E_pos = create_letter_E(DRONES_PER_LETTER, letter_positions[2])
            letter_M_pos = create_letter_M(DRONES_PER_LETTER, letter_positions[3])
            
            # Positions initiales (étoiles dispersées à basse altitude)
            initial_pos = np.zeros((num, 3))
            phi = rng.uniform(0, 2 * np.pi, num)
            r = rng.uniform(30, 100, num)
            initial_pos[:, 0] = r * np.cos(phi)
            initial_pos[:, 1] = rng.uniform(20, 45, num)  # Basse altitude
            initial_pos[:, 2] = r * np.sin(phi) * 0.5
            
            # Interpolation ease-out cubic
            def ease_out_cubic(x):
                return 1.0 - pow(1.0 - x, 3)
            
            def get_letter_progress(start_time, duration=0.8):
                if local_t < start_time:
                    return 0.0
                return min(1.0, (local_t - start_time) / duration)
            
            progress_A = ease_out_cubic(get_letter_progress(LETTER_A_START))
            progress_N = ease_out_cubic(get_letter_progress(LETTER_N_START))
            progress_E = ease_out_cubic(get_letter_progress(LETTER_E_START))
            progress_M = ease_out_cubic(get_letter_progress(LETTER_M_START))
            
            # Assigner les drones aux lettres
            # Lettre A (0-199)
            pos[0:200] = initial_pos[0:200] * (1 - progress_A) + letter_A_pos * progress_A
            cols[0:200] = BLANC * (0.2 + 0.8 * progress_A)
            
            # Lettre N (200-399)
            pos[200:400] = initial_pos[200:400] * (1 - progress_N) + letter_N_pos * progress_N
            cols[200:400] = ORANGE_NIGER * (0.2 + 0.8 * progress_N)
            
            # Lettre E (400-599)
            pos[400:600] = initial_pos[400:600] * (1 - progress_E) + letter_E_pos * progress_E
            cols[400:600] = VERT_NIGER * (0.2 + 0.8 * progress_E)
            
            # Lettre M (600-799)
            pos[600:800] = initial_pos[600:800] * (1 - progress_M) + letter_M_pos * progress_M
            cols[600:800] = BLANC * (0.2 + 0.8 * progress_M)
            
            # Étoiles de fond (800-999)
            pos[800:] = initial_pos[800:]
            twinkle = 0.3 + 0.2 * np.sin(t * 3.0 + np.arange(800, num) * 0.3)
            cols[800:] = BLANC * twinkle[:, None]
            
            # Pulsation après formation complète
            if local_t > 4.0:
                pulse = 1.0 + 0.15 * np.sin((local_t - 4.0) * 2 * np.pi)
                cols[:800] *= pulse
            
            # Jitter organique
            pos += rng.normal(0, 0.3, (num, 3))
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 3 : ORBE SOLAIRE (8-12s) - Altitude 60m
        # "Sphère dorée pulsante à hauteur raisonnable"
        # ═══════════════════════════════════════════════════════════════
        
        elif current_phase == "COEUR_COSMIQUE":
            local_t = t - PHASE_2_END
            CENTER = np.array([0.0, ALTITUDE_SPHERE, 0.0])  # 60m
            
            base_radius = 25.0  # Sphère de 25m de rayon
            
            # Convergence spirale (0-1s)
            if local_t < 1.0:
                convergence = local_t
                
                # Positions initiales (depuis les lettres ANEM)
                phi_init = rng.uniform(0, 2 * np.pi, num)
                r_init = rng.uniform(40, 80, num)
                y_init = rng.uniform(25, 55, num)  # Altitude du texte
                
                # Spirale vers le centre
                spiral_angle = convergence * 4 * np.pi + np.arange(num) * 0.01
                final_r = r_init * (1 - convergence) + base_radius * convergence
                
                pos[:, 0] = final_r * np.cos(phi_init + spiral_angle) * (1 - convergence * 0.5)
                pos[:, 1] = y_init * (1 - convergence) + CENTER[1] * convergence
                pos[:, 2] = final_r * np.sin(phi_init + spiral_angle) * (1 - convergence * 0.5)
                
                cols[:] = OR_SOLEIL * (0.5 + 0.5 * convergence)
            
            else:
                # Sphère formée avec pulsations
                phi = rng.uniform(0, 2 * np.pi, num)
                cos_theta = rng.uniform(-1, 1, num)
                theta = np.arccos(cos_theta)
                
                # Trois pulsations de cœur
                pulse_t = local_t - 1.0
                pulse1 = np.exp(-((pulse_t - 0.5) ** 2) / 0.05) * 5.0
                pulse2 = np.exp(-((pulse_t - 1.5) ** 2) / 0.05) * 7.0
                pulse3 = np.exp(-((pulse_t - 2.5) ** 2) / 0.05) * 10.0
                
                total_pulse = pulse1 + pulse2 + pulse3
                current_radius = base_radius * (1.0 + total_pulse * 0.08)
                
                pos[:, 0] = CENTER[0] + current_radius * np.sin(theta) * np.cos(phi)
                pos[:, 1] = CENTER[1] + current_radius * np.sin(theta) * np.sin(phi)
                pos[:, 2] = CENTER[2] + current_radius * np.cos(theta)
                
                base_intensity = 1.0 + total_pulse * 0.4
                cols[:] = OR_SOLEIL * base_intensity
                cols = np.clip(cols, 0, 2.5)
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 4 : ARC-EN-CIEL TERRESTRE (12-20s) - Altitude 20-50m
        # "Comme un pont lumineux au-dessus du public"
        # ═══════════════════════════════════════════════════════════════
        
        elif current_phase == "ECLOSION_FINALE":
            local_t = t - PHASE_3_END
            
            EXPLOSION_DURATION = 0.5
            RAINBOW_FORM_END = 2.0
            RAINBOW_HOLD_END = 6.0
            TRANSITION_END = 8.0
            
            # Arc-en-ciel BAS et LARGE (comme un pont)
            rainbow_width = 140.0   # 140m de large
            arc_base_height = 20.0  # Base à 20m
            arc_max_height = 50.0   # Sommet à 50m
            arc_z_position = -20.0  # DEVANT le spectateur
            
            # Explosion (0-0.5s)
            if local_t < EXPLOSION_DURATION:
                explosion_progress = local_t / EXPLOSION_DURATION
                
                # Direction depuis le centre (60m)
                phi = rng.uniform(0, 2 * np.pi, num)
                theta = rng.uniform(0.3, 1.2, num)  # Principalement vers le bas/côtés
                
                initial_speed = 40.0
                distance = initial_speed * explosion_progress * (0.7 + 0.3 * rng.uniform(0, 1, num))
                
                pos[:, 0] = distance * np.sin(theta) * np.cos(phi)
                pos[:, 1] = ALTITUDE_SPHERE + distance * np.cos(theta) * 0.3  # Descend
                pos[:, 2] = distance * np.sin(theta) * np.sin(phi)
                
                flash_intensity = 2.0 * (1 - explosion_progress) + 1.0
                cols[:] = BLANC * flash_intensity
            
            # Formation arc-en-ciel BAS (0.5-2.0s)
            elif local_t < RAINBOW_FORM_END:
                form_progress = (local_t - EXPLOSION_DURATION) / (RAINBOW_FORM_END - EXPLOSION_DURATION)
                form_ease = form_progress * form_progress * (3.0 - 2.0 * form_progress)
                
                drones_per_band = num // 7
                
                # Position explosée
                exploded_pos = np.zeros((num, 3))
                phi = rng.uniform(0, 2 * np.pi, num)
                r = 30 + 30 * rng.uniform(0, 1, num)
                exploded_pos[:, 0] = r * np.cos(phi)
                exploded_pos[:, 1] = 40 + r * rng.uniform(-0.3, 0.3, num)
                exploded_pos[:, 2] = r * np.sin(phi) * 0.5
                
                # Position finale : arc-en-ciel BAS
                rainbow_pos = np.zeros((num, 3))
                
                for band_idx in range(7):
                    start_idx = band_idx * drones_per_band
                    end_idx = start_idx + drones_per_band if band_idx < 6 else num
                    band_count = end_idx - start_idx
                    
                    # Arc de cercle horizontal (pont)
                    arc_angles = np.linspace(0, np.pi, band_count)
                    band_height_offset = band_idx * 4  # Bandes empilées
                    
                    rainbow_pos[start_idx:end_idx, 0] = (rainbow_width / 2) * np.cos(arc_angles)
                    # Hauteur : arc de 20m à 50m
                    rainbow_pos[start_idx:end_idx, 1] = arc_base_height + np.sin(arc_angles) * (arc_max_height - arc_base_height) + band_height_offset
                    rainbow_pos[start_idx:end_idx, 2] = arc_z_position + rng.uniform(-2, 2, band_count)
                    
                    cols[start_idx:end_idx] = RAINBOW_COLORS[band_idx]
                
                pos = exploded_pos * (1 - form_ease) + rainbow_pos * form_ease
                cols *= (0.5 + 0.5 * form_ease)
            
            # Arc-en-ciel stable BAS (2.0-6.0s)
            elif local_t < RAINBOW_HOLD_END:
                drones_per_band = num // 7
                
                for band_idx in range(7):
                    start_idx = band_idx * drones_per_band
                    end_idx = start_idx + drones_per_band if band_idx < 6 else num
                    band_count = end_idx - start_idx
                    
                    arc_angles = np.linspace(0, np.pi, band_count)
                    band_height_offset = band_idx * 4
                    
                    # Légère ondulation vivante
                    wave = np.sin(arc_angles * 2 + t * 0.5) * 1.5
                    
                    pos[start_idx:end_idx, 0] = (rainbow_width / 2) * np.cos(arc_angles)
                    pos[start_idx:end_idx, 1] = arc_base_height + np.sin(arc_angles) * (arc_max_height - arc_base_height) + band_height_offset + wave
                    pos[start_idx:end_idx, 2] = arc_z_position + np.sin(arc_angles * 3 + t * 0.3) * 2.0
                    
                    pulse = 0.9 + 0.1 * np.sin(t * 2.0 + band_idx * 0.5)
                    cols[start_idx:end_idx] = RAINBOW_COLORS[band_idx] * pulse
            
            # Transition vers désert (6.0-8.0s)
            else:
                transition_progress = (local_t - RAINBOW_HOLD_END) / (TRANSITION_END - RAINBOW_HOLD_END)
                transition_ease = transition_progress * transition_progress
                
                drones_per_band = num // 7
                
                DESERT_COLORS = np.array([
                    [0.96, 0.64, 0.38],
                    [0.87, 0.53, 0.25],
                    [0.82, 0.41, 0.12],
                ])
                
                for band_idx in range(7):
                    start_idx = band_idx * drones_per_band
                    end_idx = start_idx + drones_per_band if band_idx < 6 else num
                    band_count = end_idx - start_idx
                    
                    arc_angles = np.linspace(0, np.pi, band_count)
                    
                    # Arc qui s'aplatit en ligne ondulante (dunes)
                    base_x = (rainbow_width / 2) * np.cos(arc_angles)
                    target_x = np.linspace(-80, 80, band_count)  # Ligne droite élargie
                    
                    base_y = arc_base_height + np.sin(arc_angles) * (arc_max_height - arc_base_height)
                    target_y = 25.0 + np.sin(np.linspace(0, 4*np.pi, band_count)) * 8  # Dunes
                    
                    pos[start_idx:end_idx, 0] = base_x * (1 - transition_ease) + target_x * transition_ease
                    pos[start_idx:end_idx, 1] = base_y * (1 - transition_ease) + target_y * transition_ease
                    pos[start_idx:end_idx, 2] = arc_z_position + transition_ease * 30
                    
                    desert_color = DESERT_COLORS[band_idx % 3]
                    cols[start_idx:end_idx] = RAINBOW_COLORS[band_idx] * (1 - transition_ease) + desert_color * transition_ease
                    cols[start_idx:end_idx] *= (1.0 - transition_ease * 0.2)
        
        # ═══════════════════════════════════════════════════════════════
        # MICRO-MOUVEMENTS ORGANIQUES
        # ═══════════════════════════════════════════════════════════════
        
        micro_x = np.sin(t * 1.5 + np.arange(num) * 0.01) * 0.3
        micro_y = np.cos(t * 1.8 + np.arange(num) * 0.015) * 0.25
        micro_z = np.sin(t * 2.2 + np.arange(num) * 0.02) * 0.2
        
        pos[:, 0] += micro_x
        pos[:, 1] += micro_y
        pos[:, 2] += micro_z
        
        # ═══════════════════════════════════════════════════════════════
        # CONTRAINTE DE SOL ABSOLUE - Jamais sous 15m
        # ═══════════════════════════════════════════════════════════════
        pos[:, 1] = np.maximum(pos[:, 1], GROUND_CLEARANCE)
        
        # ═══════════════════════════════════════════════════════════════
        # AUDIO-RÉACTIVITÉ
        # ═══════════════════════════════════════════════════════════════
        
        audio_energy = getattr(self, 'audio_energy', 0.5)
        if audio_energy > 0.65:
            cols *= (1.0 + (audio_energy - 0.65) * 0.4)
        
        cols = np.clip(cols, 0.0, 3.0)
        
        return pos, cols

    def _act_1_desert(self, num, t=0.0):
        """
        ACTE 1 : DUNES DU SAHARA - Version Simple et Élégante
        Grille avec sculpture sinusoïdale, motifs Touareg
        """
        bass_energy = 0.5 + 0.3 * np.sin(t * 3.0)
        
        # 1. Grille de base
        grid_side = int(np.ceil(np.sqrt(num))) + 1
        x = np.linspace(-120, 120, grid_side)
        z = np.linspace(-120, 120, grid_side)
        xv, zv = np.meshgrid(x, z)
        
        pos = np.zeros((num, 3))
        flat_x = xv.flatten()
        flat_z = zv.flatten()
        
        pos[:, 0] = flat_x[:num]
        pos[:, 2] = flat_z[:num]
        
        # 2. Sculpture des Dunes (Multi-Layer)
        amp_bass = 1.0 + bass_energy * 1.5 
        
        freq_dune = 0.04
        freq_ripple = 0.12
        
        # Grandes dunes respirantes (hauteur réaliste 15-45m)
        y_dunes = 20.0 * np.sin(pos[:, 0] * freq_dune + t * 0.5) * np.cos(pos[:, 2] * freq_dune + t * 0.3)
        
        # Dunes secondaires
        y_dunes2 = 10.0 * np.sin(pos[:, 0] * 0.06 + pos[:, 2] * 0.04 + t * 0.4)
        
        # Rides de sable (vent)
        y_ripples = 3.0 * np.sin(pos[:, 0] * freq_ripple + pos[:, 2] * freq_ripple + t * 2.5)
        
        # Base à 20m d'altitude
        pos[:, 1] = 20.0 + (y_dunes + y_dunes2) * amp_bass + y_ripples

        # 3. Couleurs - Motif Sahélien
        cols = np.tile(self.colors["soleil_or"], (num, 1))
        
        # Bandes diagonales (Zébrures Touareg)
        pattern_mask = (np.abs(pos[:, 0] + pos[:, 2]) % 50.0) < 18.0
        
        # Sommets brillants
        peaks_mask = pos[:, 1] > (25.0 + 12.0 * amp_bass)
        
        # Application couleurs
        cols[pattern_mask] = self.colors["orange_niger"] 
        cols[peaks_mask] = self.colors["blanc_pure"]
        
        # Contrainte de sol - minimum 10m
        pos[:, 1] = np.maximum(pos[:, 1], 10.0)
        
        return pos, cols

    def _act_2_desert_seveille(self, num, t=0.0):
        """
        ═══════════════════════════════════════════════════════════════════════
        ACTE 2 : LE DÉSERT S'ÉVEILLE - NAISSANCE DES DUNES
        ═══════════════════════════════════════════════════════════════════════
        
        Le désert se crée sous nos yeux, grain par grain, jusqu'à former
        un Sahara nigérien VIVANT et RESPIRANT.
        
        CHRONOLOGIE (15 secondes):
        ─────────────────────────────────────────────────────────────────────
        PARTIE 1 - NAISSANCE DU SABLE (0-4s)
          0-1s : Nuage de grains apparaît (poussière cosmique)
          1-2s : Sédimentation (grains tombent par gravité)
          2-3s : Premières rides se forment
          3-4s : Organisation en micro-dunes
        
        PARTIE 2 - CROISSANCE DES DUNES (4-9s)
          4-5s : Dunes barkhanes émergent (croissants migrants)
          5-6s : Dunes transversales se gonflent (respirantes)
          6-7s : Dune étoilée commence à tourner
          7-8s : Erg ondulant entre en danse
          8s   : LA CARAVANE APPARAÎT à l'horizon
        
        PARTIE 3 - VIE DU DÉSERT (9-13s)
          9-10s  : Vent dominant s'installe + rafales
          10-11s : Vague de sable traverse l'écran
          11-13s : Couleurs virent au coucher de soleil
        
        PARTIE 4 - TRANSITION MAGIQUE (13-15s)
          13-14s : Dunes s'aplatissent progressivement
          14-15s : Forme de fleuve apparaît → ACTE 3
        ═══════════════════════════════════════════════════════════════════════
        """
        
        # Générateur reproductible
        rng = np.random.default_rng(42)
        
        # Initialisation
        pos = np.zeros((num, 3))
        cols = np.zeros((num, 3))
        
        # ═══════════════════════════════════════════════════════════════════
        # PALETTE "DÉSERT VIVANT"
        # ═══════════════════════════════════════════════════════════════════
        SABLE_HUMIDE = np.array([0.75, 0.45, 0.15])    # Bas des dunes
        SABLE_MOYEN = np.array([0.85, 0.55, 0.25])     # Flancs
        SABLE_SEC = np.array([0.95, 0.65, 0.35])       # Hauts
        CRETE_SOLEIL = np.array([1.0, 0.75, 0.45])     # Crêtes ensoleillées
        ORANGE_NIGER = np.array([1.0, 0.5, 0.0])       # Identité nationale
        OR_COUCHANT = np.array([1.0, 0.4, 0.1])        # Coucher de soleil
        VIOLET_OMBRE = np.array([0.5, 0.25, 0.4])      # Ombres profondes
        
        # ═══════════════════════════════════════════════════════════════════
        # SYSTÈME DE VENT GLOBAL
        # ═══════════════════════════════════════════════════════════════════
        vent_direction_x = np.cos(t * 0.1) * 0.8 + 0.2
        vent_direction_z = np.sin(t * 0.08) * 0.4
        vent_vitesse = 0.8 + np.sin(t * 0.3) * 0.4
        turbulence = 0.5 + np.sin(t * 0.7) * 0.3
        
        # Position du "soleil" virtuel pour l'éclairage
        soleil_altitude = 30 + np.sin(t * 0.1) * 10
        soleil_azimuth = t * 0.2
        
        # ═══════════════════════════════════════════════════════════════════
        # PARTIE 1 : NAISSANCE DU SABLE (0-4s)
        # ═══════════════════════════════════════════════════════════════════
        if t < 4.0:
            
            # Phase 1a : Nuage de grains (0-1s)
            if t < 1.0:
                progression = t / 1.0
                n_visible = int(progression * num)
                
                # Apparition dans une sphère de poussière cosmique
                for i in range(num):
                    if i < n_visible:
                        # Sphère de rayon 80m
                        theta = rng.uniform(0, 2 * np.pi)
                        phi = rng.uniform(0, np.pi)
                        r = rng.uniform(20, 80)
                        
                        pos[i, 0] = r * np.sin(phi) * np.cos(theta)
                        pos[i, 1] = 40 + r * np.cos(phi) * 0.5  # Centre à 40m
                        pos[i, 2] = r * np.sin(phi) * np.sin(theta)
                        
                        # Scintillement de poussière
                        cols[i] = SABLE_SEC * (0.5 + rng.uniform(0, 0.5))
                    else:
                        pos[i] = [0, -100, 0]  # Caché
                        cols[i] = [0, 0, 0]
            
            # Phase 1b : Sédimentation (1-2s)
            elif t < 2.0:
                progression = (t - 1.0) / 1.0
                
                for i in range(num):
                    # Position initiale (reprendre du nuage)
                    theta = rng.uniform(0, 2 * np.pi)
                    phi = rng.uniform(0, np.pi)
                    r = rng.uniform(20, 80)
                    
                    x_init = r * np.sin(phi) * np.cos(theta)
                    y_init = 40 + r * np.cos(phi) * 0.5
                    z_init = r * np.sin(phi) * np.sin(theta)
                    
                    # Vitesse de chute variable (grains lourds vs légers)
                    vitesse_chute = 0.5 + rng.uniform(0, 1.5) * (i % 10) / 10
                    
                    # Position interpolée vers le sol
                    y_cible = 15 + rng.uniform(-3, 3)
                    
                    pos[i, 0] = x_init + vent_direction_x * progression * 10
                    pos[i, 1] = y_init - (y_init - y_cible) * progression * vitesse_chute
                    pos[i, 2] = z_init + vent_direction_z * progression * 8
                    
                    # Couleur selon la hauteur
                    h_norm = (pos[i, 1] - 10) / 40
                    cols[i] = SABLE_HUMIDE * (1 - h_norm) + SABLE_SEC * h_norm
            
            # Phase 1c : Premières rides (2-3s)
            elif t < 3.0:
                progression = (t - 2.0) / 1.0
                
                # Grille de base qui se forme
                grid_side = int(np.ceil(np.sqrt(num))) + 1
                x_lin = np.linspace(-100, 100, grid_side)
                z_lin = np.linspace(-100, 100, grid_side)
                xv, zv = np.meshgrid(x_lin, z_lin)
                flat_x = xv.flatten()[:num]
                flat_z = zv.flatten()[:num]
                
                for i in range(num):
                    # Transition douce vers la grille
                    x_random = rng.uniform(-100, 100)
                    z_random = rng.uniform(-100, 100)
                    
                    pos[i, 0] = x_random * (1 - progression) + flat_x[i % len(flat_x)] * progression
                    pos[i, 2] = z_random * (1 - progression) + flat_z[i % len(flat_z)] * progression
                    
                    # Premières rides de sable (micro-ondulations)
                    ride_amp = progression * 3.0
                    pos[i, 1] = 15 + np.sin(pos[i, 0] * 0.1) * ride_amp + np.sin(pos[i, 2] * 0.08) * ride_amp * 0.7
                    
                    cols[i] = SABLE_MOYEN
            
            # Phase 1d : Micro-dunes (3-4s)
            else:
                progression = (t - 3.0) / 1.0
                
                grid_side = int(np.ceil(np.sqrt(num))) + 1
                x_lin = np.linspace(-100, 100, grid_side)
                z_lin = np.linspace(-100, 100, grid_side)
                xv, zv = np.meshgrid(x_lin, z_lin)
                
                flat_x = xv.flatten()
                flat_z = zv.flatten()
                pos[:, 0] = flat_x[:num]
                pos[:, 2] = flat_z[:num]
                
                # Micro-dunes qui grossissent
                dune_amp = 5.0 + progression * 10.0
                pos[:, 1] = 15 + dune_amp * np.sin(pos[:, 0] * 0.05 + t * 0.3) * np.cos(pos[:, 2] * 0.04)
                pos[:, 1] += 3.0 * np.sin(pos[:, 0] * 0.12 + pos[:, 2] * 0.1)
                
                # Gradient de couleur
                h_norm = np.clip((pos[:, 1] - 10) / 25, 0, 1)
                for i in range(num):
                    cols[i] = SABLE_HUMIDE * (1 - h_norm[i]) + SABLE_SEC * h_norm[i]
        
        # ═══════════════════════════════════════════════════════════════════
        # PARTIE 2 : CROISSANCE DES DUNES (4-9s)
        # ═══════════════════════════════════════════════════════════════════
        elif t < 9.0:
            
            # Distribution des drones
            n_barkhanes = 180       # Croissants migrants
            n_transversales = 280   # Vagues respirantes
            n_etoilee = 140         # Centre rotatif
            n_reg = 180             # Plateau + inselbergs
            n_erg = 140             # Mer ondulante
            n_caravane = 20         # Caravane nomade (apparaît à t=8s)
            n_extra = num - n_barkhanes - n_transversales - n_etoilee - n_reg - n_erg - n_caravane
            
            idx = 0
            progression_globale = (t - 4.0) / 5.0  # 0 à 1 sur 4-9s
            
            # ─────────────────────────────────────────────────────────────────
            # 1. DUNES BARKHANES "MIGRANTES" (croissants qui avancent)
            # ─────────────────────────────────────────────────────────────────
            barkhane_centers = [(-60, -40), (50, 30), (-20, 60)]
            drones_per_barkhane = n_barkhanes // 3
            
            emergence_barkhane = min(1.0, (t - 4.0) / 1.0)  # Émergence en 1s
            
            for bi, (cx, cz) in enumerate(barkhane_centers):
                for i in range(drones_per_barkhane):
                    if idx >= num:
                        break
                    
                    angle = (i / drones_per_barkhane) * 2 * np.pi
                    rayon = 30 * (1 - 0.35 * np.cos(angle))
                    
                    # MIGRATION : avance vers l'Est
                    migration = (t - 4.0) * 0.8
                    
                    pos[idx, 0] = cx + np.cos(angle) * rayon + migration
                    pos[idx, 2] = cz + np.sin(angle) * rayon
                    
                    # Profil de croissant
                    hauteur_base = 20 + bi * 5
                    profil = 0.3 + 0.7 * np.sin(angle * 0.5 + np.pi/4) ** 2
                    pos[idx, 1] = (hauteur_base + profil * 22) * emergence_barkhane
                    
                    # Sable qui vole sur les crêtes
                    if pos[idx, 1] > 28:
                        pos[idx, 1] += np.sin(t * 5 + pos[idx, 0] * 0.1) * 1.5
                    
                    # Couleur chaude
                    h = (pos[idx, 1] - 15) / 30
                    cols[idx] = SABLE_MOYEN * (1 - h) + CRETE_SOLEIL * h
                    
                    idx += 1
            
            # ─────────────────────────────────────────────────────────────────
            # 2. DUNES TRANSVERSALES "RESPIRANTES" (gonflent/dégonflent)
            # ─────────────────────────────────────────────────────────────────
            n_waves = 5
            points_per_wave = n_transversales // n_waves
            
            emergence_trans = min(1.0, (t - 5.0) / 1.0) if t > 5.0 else 0.0
            
            for wave_idx in range(n_waves):
                z_base = -50 + wave_idx * 25
                
                for i in range(points_per_wave):
                    if idx >= num:
                        break
                    
                    x = (i / points_per_wave - 0.5) * 140
                    
                    # RESPIRATION : amplitude qui varie comme des poumons
                    amplitude_respiration = 22 + np.sin(t * 0.8 + wave_idx) * 6
                    
                    y = amplitude_respiration * np.sin(x * 0.08 + wave_idx * 0.5 + t * 0.3)
                    y = (y + 25) * emergence_trans
                    
                    pos[idx, 0] = x
                    pos[idx, 1] = max(12, y)
                    pos[idx, 2] = z_base + rng.uniform(-4, 4)
                    
                    # Couleur selon phase de respiration
                    respiration_phase = np.sin(t * 0.8 + wave_idx)
                    if respiration_phase > 0.5:
                        cols[idx] = CRETE_SOLEIL
                    else:
                        cols[idx] = SABLE_SEC
                    
                    idx += 1
            
            # ─────────────────────────────────────────────────────────────────
            # 3. DUNE ÉTOILÉE "ROTATIVE" (tourne sur elle-même)
            # ─────────────────────────────────────────────────────────────────
            centre_x, centre_z = 0, 0
            n_bras = 6
            points_per_bras = n_etoilee // n_bras
            
            emergence_etoile = min(1.0, (t - 6.0) / 1.0) if t > 6.0 else 0.0
            angle_rotation = t * 0.25  # Rotation lente
            
            for bras in range(n_bras):
                angle_bras = (bras / n_bras) * 2 * np.pi + angle_rotation
                
                for i in range(points_per_bras):
                    if idx >= num:
                        break
                    
                    distance = i * 2.2
                    
                    # Ondulation du bras
                    angle_var = angle_bras + np.sin(distance * 0.12) * 0.15
                    
                    pos[idx, 0] = centre_x + np.cos(angle_var) * distance
                    pos[idx, 2] = centre_z + np.sin(angle_var) * distance
                    
                    # Hauteur décroissante (sommet au centre)
                    hauteur = 45 * np.exp(-distance / 22) + 15
                    pos[idx, 1] = hauteur * emergence_etoile
                    
                    # Couleur dorée au centre
                    if distance < 15:
                        cols[idx] = ORANGE_NIGER
                    else:
                        cols[idx] = SABLE_SEC
                    
                    idx += 1
            
            # ─────────────────────────────────────────────────────────────────
            # 4. REG "TECTONIQUE" (plaques qui dérivent + inselbergs)
            # ─────────────────────────────────────────────────────────────────
            n_surface = int(n_reg * 0.7)
            n_inselbergs = n_reg - n_surface
            
            # Surface plate avec dérive tectonique
            for i in range(n_surface):
                if idx >= num:
                    break
                
                base_x = rng.uniform(-90, 90)
                base_z = rng.uniform(50, 100)
                
                # Dérive des plaques
                derive_x = np.sin(t * 0.2) * 8
                derive_z = np.cos(t * 0.15) * 6
                
                pos[idx, 0] = base_x + derive_x
                pos[idx, 1] = 10 + rng.uniform(-2, 2)
                pos[idx, 2] = base_z + derive_z
                
                cols[idx] = SABLE_HUMIDE
                idx += 1
            
            # Inselbergs qui "poussent"
            inselberg_locs = [(60, 70), (-50, 80), (20, 90), (-30, 65)]
            drones_per_insel = n_inselbergs // 4
            
            for (ix, iz) in inselberg_locs:
                for i in range(drones_per_insel):
                    if idx >= num:
                        break
                    
                    angle = rng.uniform(0, 2 * np.pi)
                    dist = rng.uniform(0, 10)
                    
                    pos[idx, 0] = ix + np.cos(angle) * dist
                    pos[idx, 2] = iz + np.sin(angle) * dist
                    
                    # Inselbergs qui "poussent" avec le temps
                    hauteur_insel = 22 * (1 - dist / 10) + np.sin(t * 0.5) * 3
                    pos[idx, 1] = 10 + hauteur_insel
                    
                    cols[idx] = SABLE_MOYEN * 0.8  # Plus sombre
                    idx += 1
            
            # ─────────────────────────────────────────────────────────────────
            # 5. ERG "DANSANT" (mer de sable ondulante)
            # ─────────────────────────────────────────────────────────────────
            emergence_erg = min(1.0, (t - 7.0) / 1.0) if t > 7.0 else 0.0
            erg_rows = 12
            erg_cols = n_erg // erg_rows
            
            for zi in range(erg_rows):
                z = -90 + zi * 8
                
                for xi in range(erg_cols):
                    if idx >= num:
                        break
                    
                    x = -90 + xi * (80.0 / erg_cols)
                    
                    # Triple sinusoïde pour effet mer agitée
                    y = (np.sin(x * 0.05 + z * 0.03 + t * 0.4) * 12 +
                         np.sin(x * 0.12 + z * 0.08 + t * 1.2) * 6 +
                         np.sin(x * 0.25 + t * 3.0) * 2 +
                         18)
                    
                    pos[idx, 0] = x
                    pos[idx, 1] = y * emergence_erg
                    pos[idx, 2] = z + rng.uniform(-2, 2)
                    
                    cols[idx] = SABLE_SEC
                    idx += 1
            
            # ─────────────────────────────────────────────────────────────────
            # 6. CARAVANE NOMADE (apparaît à t=8s)
            # ─────────────────────────────────────────────────────────────────
            if t >= 8.0:
                caravane_visible = min(1.0, (t - 8.0) / 0.5)
                
                # Position de tête
                tete_x = -70 + (t - 8.0) * 3  # Avance à 3 m/s
                tete_z = 25
                
                for i in range(n_caravane):
                    if idx >= num:
                        break
                    
                    # Ligne de "chameaux"
                    decalage = i * -3.5
                    
                    x = tete_x + decalage
                    z = tete_z + np.sin(i * 0.5) * 2.5
                    
                    # Hauteur du terrain + 2m
                    terrain_h = 15 + 8 * np.sin(x * 0.04) * np.cos(z * 0.03)
                    y = terrain_h + 2.5
                    
                    # Animation de marche
                    y += np.sin(t * 4 + i * 0.3) * 0.7
                    
                    pos[idx, 0] = x
                    pos[idx, 1] = y * caravane_visible
                    pos[idx, 2] = z
                    
                    # Couleur sombre (silhouettes)
                    cols[idx] = np.array([0.3, 0.2, 0.1])
                    idx += 1
            else:
                # Caravane pas encore visible - remplir avec extras
                for i in range(n_caravane):
                    if idx >= num:
                        break
                    pos[idx] = [rng.uniform(-80, 80), 12, rng.uniform(-80, 80)]
                    cols[idx] = SABLE_MOYEN
                    idx += 1
            
            # Remplir les extras
            while idx < num:
                pos[idx] = [rng.uniform(-90, 90), 12 + rng.uniform(-2, 4), rng.uniform(-90, 90)]
                cols[idx] = SABLE_MOYEN
                idx += 1
        
        # ═══════════════════════════════════════════════════════════════════
        # PARTIE 3 : VIE DU DÉSERT (9-13s)
        # ═══════════════════════════════════════════════════════════════════
        elif t < 13.0:
            
            # Reprendre la structure des dunes de la partie 2
            # mais avec animations vent + vague + coucher de soleil
            
            grid_side = int(np.ceil(np.sqrt(num))) + 1
            x_lin = np.linspace(-100, 100, grid_side)
            z_lin = np.linspace(-100, 100, grid_side)
            xv, zv = np.meshgrid(x_lin, z_lin)
            
            flat_x = xv.flatten()
            flat_z = zv.flatten()
            pos[:, 0] = flat_x[:num]
            pos[:, 2] = flat_z[:num]
            
            # Terrain de base (multi-dunes)
            pos[:, 1] = 18 + 18 * np.sin(pos[:, 0] * 0.04 + t * 0.3) * np.cos(pos[:, 2] * 0.035)
            pos[:, 1] += 8 * np.sin(pos[:, 0] * 0.08 + pos[:, 2] * 0.06 + t * 0.5)
            pos[:, 1] += 3 * np.sin(pos[:, 0] * 0.15 + t * 2.0)
            
            # ─────────────────────────────────────────────────────────────────
            # EFFET VENT avec rafales
            # ─────────────────────────────────────────────────────────────────
            facteur_hauteur = np.clip((pos[:, 1] - 15) / 30, 0, 1)
            
            # Vent de base (plus fort en haut)
            pos[:, 0] += vent_direction_x * vent_vitesse * facteur_hauteur * 0.8
            pos[:, 2] += vent_direction_z * vent_vitesse * facteur_hauteur * 0.6
            
            # Turbulence
            pos[:, 0] += np.sin(t * 3 + pos[:, 1] * 0.1) * turbulence * facteur_hauteur * 0.5
            pos[:, 2] += np.cos(t * 2.7 + pos[:, 0] * 0.08) * turbulence * facteur_hauteur * 0.4
            
            # Rafales locales (4 points)
            rafale_centres = [(-40, -30), (50, 20), (-20, 50), (30, -40)]
            for (rx, rz) in rafale_centres:
                distance = np.sqrt((pos[:, 0] - rx)**2 + (pos[:, 2] - rz)**2)
                mask_rafale = distance < 25
                
                rafale_force = 1.5 + np.sin(t * 2) * 0.8
                rafale_effet = (1 - distance[mask_rafale] / 25) * rafale_force
                
                pos[mask_rafale, 0] += vent_direction_x * rafale_effet * 0.4
                pos[mask_rafale, 2] += vent_direction_z * rafale_effet * 0.3
                pos[mask_rafale, 1] += np.sin(t * 8) * rafale_effet * 0.5
            
            # ─────────────────────────────────────────────────────────────────
            # VAGUE DE SABLE GÉANTE (t=10-11s)
            # ─────────────────────────────────────────────────────────────────
            if 10.0 <= t <= 11.5:
                progression_vague = (t - 10.0) / 1.5
                
                # Position de la crête
                crete_x = -100 + progression_vague * 200
                
                distance_crete = np.abs(pos[:, 0] - crete_x)
                mask_vague = distance_crete < 35
                
                # Forme de vague
                amplitude_vague = 15 * (1 - distance_crete[mask_vague] / 35)
                decalage_vague = amplitude_vague * np.sin((pos[mask_vague, 0] - crete_x) * 0.15)
                
                pos[mask_vague, 1] += decalage_vague
                
                # Crête qui explose
                mask_crete = distance_crete < 8
                pos[mask_crete, 1] += np.sin(t * 12) * 4
                pos[mask_crete, 0] += np.sin(t * 15) * 0.8
            
            # ─────────────────────────────────────────────────────────────────
            # COULEURS COUCHER DE SOLEIL
            # ─────────────────────────────────────────────────────────────────
            progression_coucher = (t - 9.0) / 4.0  # 0 à 1 sur 9-13s
            
            # Normaliser la hauteur
            h_norm = np.clip((pos[:, 1] - 10) / 35, 0, 1)
            
            for i in range(num):
                h = h_norm[i]
                
                # Gradient de base
                if h < 0.3:
                    base = SABLE_HUMIDE
                elif h < 0.6:
                    blend = (h - 0.3) / 0.3
                    base = SABLE_HUMIDE * (1 - blend) + SABLE_SEC * blend
                else:
                    blend = (h - 0.6) / 0.4
                    base = SABLE_SEC * (1 - blend) + CRETE_SOLEIL * blend
                
                # Transition vers orange/rouge (coucher de soleil)
                if h > 0.4:
                    orange_blend = progression_coucher * (h - 0.4) * 1.5
                    base = base * (1 - orange_blend) + OR_COUCHANT * orange_blend
                
                # Ombres violettes en bas
                if h < 0.25:
                    ombre_blend = progression_coucher * 0.4
                    base = base * (1 - ombre_blend) + VIOLET_OMBRE * ombre_blend
                
                cols[i] = base
            
            # Miroitement du sable
            miroitement = np.sin(pos[:, 0] * 0.2 + pos[:, 2] * 0.15 + t * 8) * 0.12
            cols[:, 0] = np.clip(cols[:, 0] + miroitement * h_norm, 0, 1.2)
            cols[:, 1] = np.clip(cols[:, 1] + miroitement * h_norm * 0.7, 0, 1.2)
            
            # Caravane (20 derniers drones)
            if t >= 9.0:
                tete_x = -70 + (t - 8.0) * 3
                tete_z = 25
                
                for i in range(20):
                    ci = num - 20 + i
                    decalage = i * -3.5
                    
                    pos[ci, 0] = tete_x + decalage
                    pos[ci, 2] = tete_z + np.sin(i * 0.5) * 2.5
                    pos[ci, 1] = 18 + 8 * np.sin(pos[ci, 0] * 0.04) + 2.5 + np.sin(t * 4 + i * 0.3) * 0.7
                    cols[ci] = np.array([0.25, 0.15, 0.08])
        
        # ═══════════════════════════════════════════════════════════════════
        # PARTIE 4 : TRANSITION MAGIQUE (13-15s)
        # ═══════════════════════════════════════════════════════════════════
        else:
            progression_trans = (t - 13.0) / 2.0  # 0 à 1 sur 13-15s
            
            grid_side = int(np.ceil(np.sqrt(num))) + 1
            x_lin = np.linspace(-100, 100, grid_side)
            z_lin = np.linspace(-100, 100, grid_side)
            xv, zv = np.meshgrid(x_lin, z_lin)
            
            flat_x = xv.flatten()
            flat_z = zv.flatten()
            pos[:, 0] = flat_x[:num]
            pos[:, 2] = flat_z[:num]
            
            # Terrain qui s'aplatit progressivement
            dune_height = 15 * (1 - progression_trans * 0.7)
            pos[:, 1] = 20 + dune_height * np.sin(pos[:, 0] * 0.04) * np.cos(pos[:, 2] * 0.035)
            
            # Forme de fleuve qui apparaît
            fleuve_mask = np.abs(pos[:, 2] - 20 * np.sin(pos[:, 0] * 0.02)) < (15 + progression_trans * 20)
            
            # Drones du fleuve descendent légèrement
            pos[fleuve_mask, 1] = pos[fleuve_mask, 1] * (1 - progression_trans * 0.3)
            
            # Couleurs
            h_norm = np.clip((pos[:, 1] - 10) / 25, 0, 1)
            
            for i in range(num):
                if fleuve_mask[i]:
                    # Transition vers bleu
                    bleu_fleuve = np.array([0.2, 0.4, 0.7])
                    cols[i] = SABLE_SEC * (1 - progression_trans) + bleu_fleuve * progression_trans
                else:
                    # Dunes qui s'assombrissent (nuit qui tombe)
                    cols[i] = SABLE_MOYEN * (1 - progression_trans * 0.4)
        
        # ═══════════════════════════════════════════════════════════════════
        # CONTRAINTES FINALES
        # ═══════════════════════════════════════════════════════════════════
        
        # Sol minimum à 8m
        pos[:, 1] = np.maximum(pos[:, 1], 8.0)
        
        # Limites spatiales
        pos[:, 0] = np.clip(pos[:, 0], -120, 120)
        pos[:, 2] = np.clip(pos[:, 2], -120, 120)
        
        # Couleurs dans les limites
        cols = np.clip(cols, 0.0, 1.5)
        
        return pos, cols

    def _act_3_fleuve_niger(self, num):
        # LE FLEUVE NIGER (The Niger River)
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
            z_final = z + perp_off + np.random.uniform(-2.0, 2.0)
            pos[i] = [x, y, z_final]
            if np.random.rand() > 0.8: cols[i] = self.colors["blanc_pure"]
        return pos, cols

    def _phase_1_pluie(self, num, t=0.0, audio_energy=0.5):
        # Cœur lumineux rouge (contour + remplissage optionnel)
        # Paramétrique: x=16 sin^3 t, y=13 cos t - 5 cos 2t - 2 cos 3t - cos 4t
        contour_ratio = 0.6
        n_contour = int(num * contour_ratio)
        n_fill = num - n_contour

        # Courbe de cœur
        ang_contour = np.linspace(0, 2*np.pi, n_contour, endpoint=False)
        x = 16 * (np.sin(ang_contour) ** 3)
        y = 13 * np.cos(ang_contour) - 5 * np.cos(2 * ang_contour) - 2 * np.cos(3 * ang_contour) - np.cos(4 * ang_contour)
        scale = 3.8  # ~120m largeur, ~100m hauteur
        x *= scale
        y *= scale

        contour_pos = np.zeros((n_contour, 3))
        contour_pos[:, 0] = x
        contour_pos[:, 1] = y

        # Remplissage
        if n_fill > 0:
            ang_fill = np.random.uniform(0, 2*np.pi, n_fill)
            r_fill = np.random.uniform(0.0, 1.0, n_fill) ** 0.6  # densité vers le bord
            fx = 16 * (np.sin(ang_fill) ** 3) * scale * r_fill
            fy = (13 * np.cos(ang_fill) - 5 * np.cos(2 * ang_fill) - 2 * np.cos(3 * ang_fill) - np.cos(4 * ang_fill)) * scale * r_fill
            fill_pos = np.zeros((n_fill, 3))
            fill_pos[:, 0] = fx
            fill_pos[:, 1] = fy
            pos = np.vstack([contour_pos, fill_pos])
        else:
            pos = contour_pos

        # Centrage scène
        center = np.array([0.0, 80.0, 0.0])
        pos += center

        # Légère épaisseur/jitter
        pos[:, 2] += np.random.uniform(-2.0, 2.0, len(pos))
        pos[:, 0] += np.random.uniform(-0.5, 0.5, len(pos))
        pos[:, 1] += np.random.uniform(-0.5, 0.5, len(pos))

        # Couleurs rouge bloom
        base_red = np.array([1.0, 0.12, 0.12], dtype=float)
        cols = np.tile(base_red, (len(pos), 1))
        pulse = 0.9 + 0.15 * np.sin(t * 2.0 + np.linspace(0, 3.14, len(pos)))
        cols *= pulse[:, None]
        cols = np.clip(cols, 0.0, 1.0)

        return pos, cols

    def _act_4_science(self, num, t=0.0, audio_energy=0.5):
        # ADN : double hélice + barreaux transversaux
        # Paramètres géométriques
        turns = 4.0
        radius = 20.0
        height = 150.0
        base_y = 20.0

        # Répartition drones : hélices 55%, barreaux 45%
        helix_ratio = 0.55
        n_helix = max(2, int(num * helix_ratio))
        n_per_helix = n_helix // 2
        n_rungs = num - 2 * n_per_helix

        # === Hélices (cyan) ===
        t_vals = np.linspace(0, turns * 2 * np.pi, n_per_helix)
        y_vals = base_y + (t_vals / (turns * 2 * np.pi)) * height
        x1 = radius * np.cos(t_vals)
        z1 = radius * np.sin(t_vals)
        x2 = radius * np.cos(t_vals + np.pi)
        z2 = radius * np.sin(t_vals + np.pi)

        helix1 = np.column_stack((x1, y_vals, z1))
        helix2 = np.column_stack((x2, y_vals, z2))

        # Pulsation lumineuse le long de l'axe
        cyan = np.array([0.05, 0.9, 1.0], dtype=float)
        pulse = 0.9 + 0.15 * np.sin(1.6 * t + (y_vals / height) * 4 * np.pi)
        cols_h1 = cyan * pulse[:, None]
        cols_h2 = cyan * pulse[:, None]

        # === Barreaux (magenta) ===
        rung_samples = 8  # points par barre
        rung_count = max(6, n_rungs // rung_samples)
        t_rung = np.linspace(0, turns * 2 * np.pi, rung_count)
        y_rung = base_y + (t_rung / (turns * 2 * np.pi)) * height
        x1_r = radius * np.cos(t_rung)
        z1_r = radius * np.sin(t_rung)
        x2_r = radius * np.cos(t_rung + np.pi)
        z2_r = radius * np.sin(t_rung + np.pi)

        s = np.linspace(0.0, 1.0, rung_samples)
        s_grid, t_grid = np.meshgrid(s, t_rung)
        s_flat = s_grid.ravel()
        t_flat = t_grid.ravel()

        x_r = np.interp(t_flat, t_rung, x1_r) * (1 - s_flat) + np.interp(t_flat, t_rung, x2_r) * s_flat
        y_r = np.interp(t_flat, t_rung, y_rung)
        z_r = np.interp(t_flat, t_rung, z1_r) * (1 - s_flat) + np.interp(t_flat, t_rung, z2_r) * s_flat

        rungs = np.column_stack((x_r, y_r, z_r))
        magenta = np.array([1.0, 0.2, 0.85], dtype=float)
        pulse_r = 0.95 + 0.18 * np.sin(2.2 * t + (y_r / height) * 3 * np.pi)
        cols_r = magenta * pulse_r[:, None]

        # Assemble
        pos = np.vstack([helix1, helix2, rungs])
        cols = np.vstack([cols_h1, cols_h2, cols_r])

        # Jitter léger pour vivant
        pos[:, 0] += np.random.uniform(-0.4, 0.4, len(pos))
        pos[:, 2] += np.random.uniform(-0.4, 0.4, len(pos))

        # Ajuster à num si surplus ou manque
        if len(pos) > num:
            pos = pos[:num]
            cols = cols[:num]
        elif len(pos) < num:
            deficit = num - len(pos)
            pos = np.vstack([pos, pos[:deficit]])
            cols = np.vstack([cols, cols[:deficit]])

        # Clamp sécurité
        cols = np.clip(cols, 0.0, 1.0)

        return pos, cols

    def _act_5_tree_of_life(self, num, t=0.0, audio_energy=0.5):
        """
        🌳 ARBRE DE VIE GÉANT LUMINEUX - Style Dubai Drone Show World Record
        
        Structure: Tronc massif brun/or, branches fractales, couronne dense verte
        Proportions: ~120m hauteur, ~100m largeur couronne
        Répartition: 30% tronc/branches, 70% couronne (feuillage)
        Effets: Micro-scintillement, bloom base, animation croissance
        """
        
        # === CACHE VÉRIFICATION ===
        cache_key = f"tree_of_life_{num}"
        if cache_key not in self._phase10_cache:
            self._phase10_cache[cache_key] = self._generate_tree_of_life_structure(num)
        
        base_pos, segment_ids, branch_heights = self._phase10_cache[cache_key]
        pos = base_pos.copy()
        
        # === PALETTE COULEURS ===
        # Tronc: brun/or lumineux #CF7A36 → #FFD700
        COL_TRUNK_BASE = np.array([0.81, 0.48, 0.21])    # #CF7A36 - brun orangé
        COL_TRUNK_GLOW = np.array([1.0, 0.84, 0.0])      # #FFD700 - or pur
        COL_BRANCH_MID = np.array([0.72, 0.60, 0.20])    # Transition brun→vert
        COL_LEAF_DARK = np.array([0.11, 0.70, 0.38])     # #1BB360 - vert profond
        COL_LEAF_BRIGHT = np.array([0.56, 1.0, 0.56])    # #90FF90 - vert éclatant
        
        # === COLORATION PAR SEGMENT ===
        cols = np.zeros((num, 3))
        
        for i in range(num):
            seg = segment_ids[i]
            h = branch_heights[i]  # Hauteur normalisée 0→1
            
            if seg == 0:  # TRONC
                # Gradient base→haut: bloom doré à la base, brun en montant
                bloom_factor = 1.0 - h  # Plus lumineux en bas
                base_col = COL_TRUNK_BASE * (1 - bloom_factor * 0.5) + COL_TRUNK_GLOW * bloom_factor * 0.5
                # Ajouter bloom intense à la base
                bloom_intensity = np.exp(-h * 3) * 0.5
                cols[i] = base_col + bloom_intensity
                
            elif seg == 1:  # BRANCHES PRINCIPALES
                # Gradient brun → vert en montant
                blend = min(1.0, h * 1.5)
                cols[i] = COL_TRUNK_BASE * (1 - blend) + COL_BRANCH_MID * blend
                
            elif seg == 2:  # BRANCHES SECONDAIRES
                # Transition vers le vert
                blend = min(1.0, h * 2)
                cols[i] = COL_BRANCH_MID * (1 - blend) + COL_LEAF_DARK * blend
                
            else:  # seg == 3: FEUILLAGE (Couronne)
                # Vert éclatant avec variations
                # Position radiale dans la couronne pour variation
                cx, cy = 0, 85  # Centre couronne
                dx, dy = pos[i, 0] - cx, pos[i, 1] - cy
                radial = np.sqrt(dx*dx + dy*dy) / 50.0  # Normalisé
                
                # Centre plus foncé, extérieur plus brillant
                blend = np.clip(radial, 0, 1)
                cols[i] = COL_LEAF_DARK * (1 - blend * 0.6) + COL_LEAF_BRIGHT * (blend * 0.6)
        
        # === ANIMATION: SCINTILLEMENT FEUILLAGE ===
        SHIMMER_FREQ = 4.0  # Hz
        SHIMMER_AMP = 0.15
        
        for i in range(num):
            if segment_ids[i] == 3:  # Feuillage uniquement
                # Phase unique par drone pour désynchronisation
                phase_offset = (pos[i, 0] * 0.1 + pos[i, 1] * 0.07) % (2 * np.pi)
                shimmer = 1.0 + SHIMMER_AMP * np.sin(2 * np.pi * SHIMMER_FREQ * t + phase_offset)
                cols[i] *= shimmer
        
        # === ANIMATION: RESPIRATION GLOBALE (audio-réactive) ===
        breath = 1.0 + 0.1 * audio_energy * np.sin(t * 2.0)
        cols *= breath
        
        # === ANIMATION: VENT DOUX SUR COURONNE ===
        WIND_FREQ = 0.5
        WIND_AMP = 2.0
        
        for i in range(num):
            if segment_ids[i] == 3:  # Feuillage
                # Déplacement horizontal ondulant
                wave_phase = pos[i, 0] * 0.03 + pos[i, 1] * 0.02
                wind_offset = WIND_AMP * np.sin(2 * np.pi * WIND_FREQ * t + wave_phase)
                pos[i, 2] += wind_offset  # Mouvement en Z (profondeur)
        
        # === ANIMATION: CROISSANCE (pour les 5 premières secondes) ===
        if t < 5.0:
            growth_progress = t / 5.0
            # Ease-in-out cubic
            growth = growth_progress * growth_progress * (3.0 - 2.0 * growth_progress)
            
            # Révéler progressivement du bas vers le haut
            for i in range(num):
                h = branch_heights[i]
                # Si la hauteur normalisée dépasse la progression, masquer
                if h > growth:
                    # Réduire la visibilité (couleur très sombre)
                    fade = max(0, 1.0 - (h - growth) * 5)
                    cols[i] *= fade
                    # Aussi comprimer vers la base
                    pos[i, 1] = pos[i, 1] * (growth * 0.5 + 0.5)
        
        # === CLAMP FINAL ===
        cols = np.clip(cols, 0.0, 1.5)  # Permettre léger HDR pour bloom
        
        return pos, cols
    
    def _generate_tree_of_life_structure(self, num):
        """
        Génère la structure statique de l'arbre:
        - Tronc cylindrique massif
        - Branches fractales en éventail
        - Couronne dense semi-elliptique
        
        Returns: (positions, segment_ids, normalized_heights)
        """
        
        # === DIMENSIONS CIBLES ===
        TREE_HEIGHT = 130.0      # Hauteur totale ~130m
        TRUNK_HEIGHT = 55.0      # Tronc jusqu'à y=60
        TRUNK_RADIUS = 10.0      # Rayon tronc base (plus épais)
        TRUNK_RADIUS_TOP = 5.0   # Rayon tronc haut
        CROWN_RADIUS_X = 60.0    # Largeur couronne ~120m total
        CROWN_RADIUS_Y = 55.0    # Hauteur couronne (ellipse plus grande)
        CROWN_CENTER_Y = 95.0    # Centre vertical couronne plus haut
        
        # === RÉPARTITION DRONES ===
        n_trunk = int(num * 0.12)        # 12% tronc
        n_branches = int(num * 0.18)     # 18% branches
        n_crown = num - n_trunk - n_branches  # 70% couronne
        
        pos = np.zeros((num, 3))
        segment_ids = np.zeros(num, dtype=int)  # 0=tronc, 1=branches1, 2=branches2, 3=feuillage
        heights = np.zeros(num)  # Hauteur normalisée pour coloration
        
        idx = 0
        
        # === 1. TRONC CYLINDRIQUE ===
        trunk_layers = 20
        drones_per_layer = n_trunk // trunk_layers
        
        for layer in range(trunk_layers):
            h_frac = layer / (trunk_layers - 1)
            y = h_frac * TRUNK_HEIGHT + 5.0  # Base à y=5
            
            # Rayon diminue vers le haut
            r = TRUNK_RADIUS * (1 - h_frac * 0.5)
            
            for j in range(drones_per_layer):
                if idx >= num:
                    break
                theta = 2 * np.pi * j / drones_per_layer
                x = r * np.cos(theta)
                z = r * np.sin(theta)
                
                pos[idx] = [x, y, z]
                segment_ids[idx] = 0
                heights[idx] = h_frac * 0.4  # Normaliser pour palette (tronc = 0-0.4)
                idx += 1
        
        # === 2. BRANCHES PRINCIPALES (Fractales niveau 1) ===
        n_main_branches = 8
        branch1_per_branch = n_branches // (n_main_branches * 2)
        
        for b in range(n_main_branches):
            theta_base = 2 * np.pi * b / n_main_branches
            
            # Point de départ: haut du tronc
            start_y = TRUNK_HEIGHT + 5
            start_x = TRUNK_RADIUS_TOP * 0.8 * np.cos(theta_base)
            start_z = TRUNK_RADIUS_TOP * 0.8 * np.sin(theta_base)
            
            # Point d'arrivée: vers l'extérieur et le haut
            end_x = CROWN_RADIUS_X * 0.6 * np.cos(theta_base)
            end_y = CROWN_CENTER_Y - 10
            end_z = CROWN_RADIUS_X * 0.4 * np.sin(theta_base)
            
            # Interpoler le long de la branche
            for j in range(branch1_per_branch):
                if idx >= num:
                    break
                t_branch = j / max(1, branch1_per_branch - 1)
                
                # Courbe légèrement courbée (Bézier quadratique simplifiée)
                mid_x = (start_x + end_x) * 0.5 + 3 * np.cos(theta_base + 0.5)
                mid_y = (start_y + end_y) * 0.5 + 8
                mid_z = (start_z + end_z) * 0.5
                
                # Interpolation quadratique
                x = (1-t_branch)**2 * start_x + 2*(1-t_branch)*t_branch * mid_x + t_branch**2 * end_x
                y = (1-t_branch)**2 * start_y + 2*(1-t_branch)*t_branch * mid_y + t_branch**2 * end_y
                z = (1-t_branch)**2 * start_z + 2*(1-t_branch)*t_branch * mid_z + t_branch**2 * end_z
                
                # Épaisseur de branche (plusieurs drones en section)
                thickness = 2.0 * (1 - t_branch * 0.7)
                offset_x = np.random.uniform(-thickness, thickness)
                offset_z = np.random.uniform(-thickness, thickness)
                
                pos[idx] = [x + offset_x, y, z + offset_z]
                segment_ids[idx] = 1
                heights[idx] = 0.4 + t_branch * 0.2  # 0.4-0.6
                idx += 1
        
        # === 3. BRANCHES SECONDAIRES ===
        n_sub_branches = 16
        branch2_per_branch = n_branches // (n_main_branches * 2) // 2
        
        for b in range(n_sub_branches):
            theta_base = 2 * np.pi * b / n_sub_branches + 0.2
            
            # Partent des branches principales
            start_y = TRUNK_HEIGHT + 15 + np.random.uniform(0, 10)
            start_x = CROWN_RADIUS_X * 0.3 * np.cos(theta_base)
            start_z = CROWN_RADIUS_X * 0.3 * np.sin(theta_base)
            
            end_x = CROWN_RADIUS_X * 0.75 * np.cos(theta_base)
            end_y = CROWN_CENTER_Y + np.random.uniform(-5, 5)
            end_z = CROWN_RADIUS_X * 0.5 * np.sin(theta_base)
            
            for j in range(branch2_per_branch):
                if idx >= num:
                    break
                t_branch = j / max(1, branch2_per_branch - 1)
                
                x = start_x + t_branch * (end_x - start_x)
                y = start_y + t_branch * (end_y - start_y)
                z = start_z + t_branch * (end_z - start_z)
                
                thickness = 1.0 * (1 - t_branch * 0.5)
                pos[idx] = [x + np.random.uniform(-thickness, thickness), 
                           y, 
                           z + np.random.uniform(-thickness, thickness)]
                segment_ids[idx] = 2
                heights[idx] = 0.6 + t_branch * 0.15  # 0.6-0.75
                idx += 1
        
        # === 4. COURONNE (FEUILLAGE) - 70% des drones ===
        # Distribution dense sur dôme semi-elliptique "nuage arrondi"
        
        remaining = num - idx
        
        # Méthode: Distribution Fibonacci sur surface de dôme 3D
        golden_angle = np.pi * (3 - np.sqrt(5))  # ~137.5°
        
        for i in range(remaining):
            if idx >= num:
                break
            
            # Spiral Fibonacci pour distribution uniforme sur dôme
            t_norm = i / remaining
            
            # Distribution en couches concentriques avec plus de drones au centre
            # Utiliser une distribution biaisée vers le centre (plus dense)
            r_base = np.sqrt(t_norm) * 0.95  # Légèrement moins que 1 pour bords doux
            theta = i * golden_angle
            
            # Coordonnées sur ellipse horizontale
            local_x = r_base * CROWN_RADIUS_X * np.cos(theta)
            
            # Hauteur: dôme parabolique - plus haut au centre
            # y = y_max - k * r^2 (paraboloïde inversé)
            height_factor = 1.0 - r_base * r_base  # 1 au centre, 0 au bord
            y_offset = CROWN_RADIUS_Y * 0.7 * height_factor
            
            # Ajouter variation verticale pour volume "nuageux"
            layer_variation = np.sin(theta * 3 + t_norm * 10) * 5
            
            y_global = CROWN_CENTER_Y + y_offset + layer_variation
            
            # Profondeur Z pour volume 3D sphérique
            # Plus de profondeur au centre, moins aux bords
            z_max = 20.0 * np.sqrt(max(0, 1 - r_base * r_base))
            z_depth = z_max * np.sin(theta * 0.7 + i * 0.1)
            z_random = np.random.uniform(-4, 4)
            
            # Ajouter irrégularités naturelles (feuillage organique)
            noise_x = np.random.uniform(-4, 4)
            noise_y = np.random.uniform(-3, 3)
            
            pos[idx] = [local_x + noise_x, y_global + noise_y, z_depth + z_random]
            segment_ids[idx] = 3
            heights[idx] = 0.75 + 0.25 * height_factor  # Plus "haut" = plus au centre
            idx += 1
        
        return pos, segment_ids, heights

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

        return self._fill_shape_uniformly(is_in_wildlife, (-80, 80, -40, 60), num, center=(0, 60, 0), z_depth=12.0)

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
                pos[idx] = [x, y, np.random.uniform(-2.0, 2.0)]
                
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

    def _act_8_finale(self, num, t=0.0):
        # "LE CŒUR DE L'AFRIQUE" (Volumétrie Pulsante)
        # A living, beating heart representing Unity.
        
        # 1. Generate Base Shape (Cached)
        if not hasattr(self, '_heart_cache'):
             self._heart_cache = {}
        
        cache_key = num
        if cache_key not in self._heart_cache:
             # 3D Heart Formula
             # (x^2 + 9/4 y^2 + z^2 - 1)^3 - x^2 z^3 - 9/80 y^2 z^3 = 0
             # We use a rejection sampling or parametric approach for better distribution
             
             pos = []
             # Parametric approximation for better point distribution
             # Using a modified sphere mapping
             count = 0
             while count < num:
                 # Random point in cube
                 x = np.random.uniform(-1.5, 1.5)
                 y = np.random.uniform(-1.5, 1.5)
                 z = np.random.uniform(-1.5, 1.5)
                 
                 # Heart equation check
                 a = x**2 + (9/4)*(y**2) + z**2 - 1
                 if a**3 - (x**2)*(z**3) - (9/80)*(y**2)*(z**3) <= 0:
                     pos.append([x, y, z])
                     count += 1
             
             pos = np.array(pos)
             # Scale up
             pos *= 35.0 
             # Center
             pos[:, 1] += 70.0
             
             self._heart_cache[cache_key] = pos
        
        base_pos = self._heart_cache[cache_key]
        
        # 2. Animation: Heartbeat (Systole/Diastole)
        # Double beat pattern: "Lub-Dub" ... pause ...
        cycle = t % 1.5 # 1.5s per beat cycle (approx 80 bpm)
        
        # Beat curve
        scale = 1.0
        if cycle < 0.2: # First beat (Lub)
            scale = 1.0 + 0.1 * np.sin(cycle * np.pi / 0.2)
        elif 0.3 < cycle < 0.5: # Second beat (Dub)
            scale = 1.0 + 0.05 * np.sin((cycle - 0.3) * np.pi / 0.2)
            
        # Apply Scale
        # We scale relative to the center of the heart (0, 70, 0)
        animated_pos = np.zeros_like(base_pos)
        animated_pos[:, 0] = base_pos[:, 0] * scale
        animated_pos[:, 1] = (base_pos[:, 1] - 70.0) * scale + 70.0
        animated_pos[:, 2] = base_pos[:, 2] * scale
        
        # 3. Color Wave (Blood flow / Energy)
        # Wave moves from bottom to top
        cols = np.zeros((num, 3))
        
        # Define colors
        col_gold = np.array(self.colors["soleil_or"])
        col_red = np.array([1.0, 0.05, 0.1]) # Deep Red
        col_core = np.array([1.0, 0.8, 0.8]) # White-ish center
        
        for i in range(num):
            # Calculate distance from center for gradient
            y_rel = animated_pos[i, 1] - 70.0
            dist = np.sqrt(animated_pos[i, 0]**2 + y_rel**2 + animated_pos[i, 2]**2)
            
            # Pulse wave traveling outwards
            wave_phase = (dist / 20.0) - (t * 2.0)
            wave_val = (np.sin(wave_phase) + 1.0) / 2.0 # 0 to 1
            
            # Mix Red and Gold based on wave
            # Core is brighter
            base_mix = col_red * 0.7 + col_gold * 0.3
            
            # Highlight pulse
            if wave_val > 0.8:
                cols[i] = col_core # Bright pulse
            else:
                cols[i] = base_mix * (0.5 + 0.5 * wave_val) # Breathing brightness
                
        return animated_pos, cols

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
                pos[idx] = [x, y, np.random.uniform(-2.0, 2.0)]
                
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
        # Precise Niger Map - High-Fidelity Image-Based Rendering
        image_path = "C:/Users/mtahiroudaouda/.gemini/antigravity/brain/1bd65539-7aec-43dc-9315-5bbdd944f9a6/uploaded_image_1766836483607.png"
        
        pos, cols = self._sample_from_image(image_path, num, target_width=165.0)
        
        if pos is None:
            # Emergency manual fallback (Old logic)
            return self._shape_sphere(num, 30, self.colors["orange_niger"])

        # Offset to clear ground and center
        center_y = 65.0
        pos[:, 1] += center_y
        
        # Apply 3D Volumetric Thickness (8m)
        z_depth = 8.0
        pos[:, 2] = np.random.uniform(-z_depth/2, z_depth/2, num)
                
        return pos, cols

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


    def _phase_8_finale(self, num, t=0.0):
        # "LE CŒUR DE L'AFRIQUE" (Volumétrie Pulsante)
        # A living, beating heart representing Unity.
        
        # 1. Generate Base Shape (Cached)
        if not hasattr(self, '_heart_cache'):
             self._heart_cache = {}
        
        cache_key = num
        if cache_key not in self._heart_cache:
             # 3D Heart Formula
             # (x^2 + 9/4 y^2 + z^2 - 1)^3 - x^2 z^3 - 9/80 y^2 z^3 = 0
             # We use a rejection sampling or parametric approach for better distribution
             
             pos = []
             # Parametric approximation for better point distribution
             # Using a modified sphere mapping
             count = 0
             while count < num:
                 # Random point in cube
                 x = np.random.uniform(-1.5, 1.5)
                 y = np.random.uniform(-1.5, 1.5)
                 z = np.random.uniform(-1.5, 1.5)
                 
                 # Heart equation check
                 a = x**2 + (9/4)*(y**2) + z**2 - 1
                 if a**3 - (x**2)*(z**3) - (9/80)*(y**2)*(z**3) <= 0:
                     pos.append([x, y, z])
                     count += 1
             
             pos = np.array(pos)
             # Scale up
             pos *= 35.0 
             # Center
             pos[:, 1] += 70.0
             
             self._heart_cache[cache_key] = pos
        
        base_pos = self._heart_cache[cache_key]
        
        # 2. Animation: Heartbeat (Systole/Diastole)
        # Double beat pattern: "Lub-Dub" ... pause ...
        cycle = t % 1.5 # 1.5s per beat cycle (approx 80 bpm)
        
        # Beat curve
        scale = 1.0
        if cycle < 0.2: # First beat (Lub)
            scale = 1.0 + 0.1 * np.sin(cycle * np.pi / 0.2)
        elif 0.3 < cycle < 0.5: # Second beat (Dub)
            scale = 1.0 + 0.05 * np.sin((cycle - 0.3) * np.pi / 0.2)
            
        # Apply Scale
        # We scale relative to the center of the heart (0, 70, 0)
        animated_pos = np.zeros_like(base_pos)
        animated_pos[:, 0] = base_pos[:, 0] * scale
        animated_pos[:, 1] = (base_pos[:, 1] - 70.0) * scale + 70.0
        animated_pos[:, 2] = base_pos[:, 2] * scale
        
        # 3. Color Wave (Blood flow / Energy)
        # Wave moves from bottom to top
        cols = np.zeros((num, 3))
        
        # Define colors
        col_gold = np.array(self.colors["soleil_or"])
        col_red = np.array([1.0, 0.05, 0.1]) # Deep Red
        col_core = np.array([1.0, 0.8, 0.8]) # White-ish center
        
        for i in range(num):
            # Calculate distance from center for gradient
            y_rel = animated_pos[i, 1] - 70.0
            dist = np.sqrt(animated_pos[i, 0]**2 + y_rel**2 + animated_pos[i, 2]**2)
            
            # Pulse wave traveling outwards
            wave_phase = (dist / 20.0) - (t * 2.0)
            wave_val = (np.sin(wave_phase) + 1.0) / 2.0 # 0 to 1
            
            # Mix Red and Gold based on wave
            # Core is brighter
            base_mix = col_red * 0.7 + col_gold * 0.3
            
            # Highlight pulse
            if wave_val > 0.8:
                cols[i] = col_core # Bright pulse
            else:
                cols[i] = base_mix * (0.5 + 0.5 * wave_val) # Breathing brightness
                
        return animated_pos, cols

    def _act_9_eagle(self, num, t=0.0):
        """
        🦅 AIGLE VIVANT EN VOL - Style Dubai/Shanghai Drone Show
        
        Structure anatomique détaillée:
        - Ailes déployées avec plumes primaires/secondaires visibles
        - Tête blanche distinctive avec bec jaune
        - Corps bronze/marron avec détails musculaires
        - Queue évasée avec plumes marquées
        - Pattes avec serres visibles
        
        Animation:
        - Battement d'ailes réaliste
        - Micro-mouvements de tête
        - Queue ondulante
        - Hover global
        """
        
        # === CACHE STRUCTURE ===
        cache_key = f"eagle_vivant_{num}"
        if cache_key not in self._phase10_cache:
            self._phase10_cache[cache_key] = self._generate_eagle_structure(num)
        
        base_pos, segment_ids, local_coords = self._phase10_cache[cache_key]
        pos = base_pos.copy()
        
        # === PALETTE COULEURS RÉALISTES ===
        COL_BRONZE_DARK = np.array([0.27, 0.13, 0.05])    # #452209 - plumes foncées
        COL_BRONZE_MID = np.array([0.63, 0.41, 0.17])     # #A1692C - corps bronze
        COL_BRONZE_LIGHT = np.array([0.78, 0.55, 0.25])   # Reflets dorés
        COL_WHITE_HEAD = np.array([1.0, 1.0, 1.0])        # Tête blanche
        COL_BEAK_YELLOW = np.array([1.0, 0.78, 0.0])      # Bec jaune/or
        COL_EYE_GOLD = np.array([1.0, 0.85, 0.2])         # Œil doré
        
        # === COLORATION PAR SEGMENT ===
        # Segments: 0=corps, 1=aile_gauche, 2=aile_droite, 3=tête, 4=bec, 5=queue, 6=pattes
        cols = np.zeros((num, 3))
        
        for i in range(num):
            seg = segment_ids[i]
            lx, ly = local_coords[i, 0], local_coords[i, 1]
            
            if seg == 0:  # CORPS
                # Gradient bronze avec effet musculaire
                blend = np.clip((ly + 20) / 40, 0, 1)
                cols[i] = COL_BRONZE_DARK * (1 - blend) + COL_BRONZE_MID * blend
                
            elif seg in [1, 2]:  # AILES
                # Dégradé du corps vers les extrémités
                dist_from_body = abs(lx) / 70.0
                # Plumes primaires (extrémités) plus foncées
                if dist_from_body > 0.7:
                    cols[i] = COL_BRONZE_DARK * 0.8
                elif dist_from_body > 0.4:
                    cols[i] = COL_BRONZE_MID
                else:
                    cols[i] = COL_BRONZE_LIGHT
                    
            elif seg == 3:  # TÊTE (blanche)
                cols[i] = COL_WHITE_HEAD
                
            elif seg == 4:  # BEC
                cols[i] = COL_BEAK_YELLOW
                
            elif seg == 5:  # QUEUE
                # Dégradé bronze foncé
                cols[i] = COL_BRONZE_DARK * 0.9 + COL_BRONZE_MID * 0.1
                
            elif seg == 6:  # PATTES
                cols[i] = COL_BEAK_YELLOW * 0.9
        
        # === ANIMATION: BATTEMENT D'AILES ===
        FLAP_FREQ = 1.2  # Hz - battement lent majestueux
        FLAP_AMP = 15.0  # Amplitude verticale
        FLAP_TWIST = 8.0  # Torsion en Z
        
        flap_phase = 2 * np.pi * FLAP_FREQ * t
        flap_wave = np.sin(flap_phase)
        flap_wave_delayed = np.sin(flap_phase - 0.3)  # Retard pour effet élastique
        
        for i in range(num):
            seg = segment_ids[i]
            lx = local_coords[i, 0]
            
            if seg in [1, 2]:  # Ailes
                # Distance normalisée depuis le corps
                dist_factor = (abs(lx) - 10) / 60.0
                dist_factor = np.clip(dist_factor, 0, 1)
                
                # Mouvement vertical (battement)
                # Utiliser retard pour effet élastique (extrémités suivent)
                wave_to_use = flap_wave * (1 - dist_factor * 0.3) + flap_wave_delayed * (dist_factor * 0.3)
                y_offset = FLAP_AMP * dist_factor * wave_to_use
                pos[i, 1] += y_offset
                
                # Torsion en Z (rotation des plumes)
                z_twist = FLAP_TWIST * dist_factor * np.cos(flap_phase)
                pos[i, 2] += z_twist
                
                # Légère compression horizontale lors du battement vers le bas
                if flap_wave < 0:
                    x_compress = 1.0 - 0.05 * abs(flap_wave) * dist_factor
                    pos[i, 0] *= x_compress
        
        # === ANIMATION: MICRO-MOUVEMENTS TÊTE ===
        HEAD_FREQ = 0.4  # Hz - lent et alerte
        HEAD_AMP_X = 2.0  # Rotation gauche/droite
        HEAD_AMP_Y = 1.0  # Inclinaison
        
        head_rotation = HEAD_AMP_X * np.sin(2 * np.pi * HEAD_FREQ * t)
        head_tilt = HEAD_AMP_Y * np.sin(2 * np.pi * HEAD_FREQ * 0.7 * t + 1.0)
        
        for i in range(num):
            if segment_ids[i] in [3, 4]:  # Tête et bec
                # Rotation horizontale
                pos[i, 0] += head_rotation
                # Inclinaison
                pos[i, 1] += head_tilt
        
        # === ANIMATION: QUEUE ONDULANTE ===
        TAIL_FREQ = 0.8
        TAIL_AMP = 3.0
        
        for i in range(num):
            if segment_ids[i] == 5:  # Queue
                ly = local_coords[i, 1]
                # Plus d'ondulation vers l'extrémité
                tail_factor = (abs(ly) - 25) / 20.0
                tail_factor = np.clip(tail_factor, 0, 1)
                tail_wave = TAIL_AMP * tail_factor * np.sin(2 * np.pi * TAIL_FREQ * t + ly * 0.1)
                pos[i, 2] += tail_wave
        
        # === ANIMATION: PATTES (ouverture/fermeture serres) ===
        CLAW_FREQ = 0.6
        claw_state = 0.5 + 0.5 * np.sin(2 * np.pi * CLAW_FREQ * t)
        
        for i in range(num):
            if segment_ids[i] == 6:  # Pattes
                lx = local_coords[i, 0]
                # Écarter/rapprocher les serres
                sign = 1 if lx > 0 else -1
                pos[i, 0] += sign * 2.0 * claw_state
        
        # === ANIMATION: HOVER GLOBAL ===
        hover = 3.0 * np.sin(t * 0.8)
        pos[:, 1] += hover
        
        # === ANIMATION: COMPRESSION CORPS (effet musculaire) ===
        body_compress = 1.0 + 0.03 * flap_wave
        for i in range(num):
            if segment_ids[i] == 0:  # Corps
                pos[i, 1] *= body_compress
        
        # === EFFETS LUMINEUX: SCINTILLEMENT PLUMES ===
        SHIMMER_FREQ = 6.0
        SHIMMER_AMP = 0.12
        
        for i in range(num):
            if segment_ids[i] in [1, 2]:  # Ailes
                phase_offset = local_coords[i, 0] * 0.05 + local_coords[i, 1] * 0.03
                shimmer = 1.0 + SHIMMER_AMP * np.sin(2 * np.pi * SHIMMER_FREQ * t + phase_offset)
                cols[i] *= shimmer
        
        # === BLOOM SUR TÊTE BLANCHE ET YEUX ===
        for i in range(num):
            if segment_ids[i] == 3:  # Tête
                # Léger bloom constant
                cols[i] *= 1.15
            elif segment_ids[i] == 4:  # Bec
                cols[i] *= 1.1
        
        # === CLAMP FINAL ===
        cols = np.clip(cols, 0.0, 1.5)
        
        return pos, cols
    
    def _generate_eagle_structure(self, num):
        """
        Génère la structure anatomique détaillée de l'aigle:
        - Corps elliptique avec volume
        - Ailes avec détails de plumes (primaires, secondaires, tertiaires)
        - Tête ronde avec collerette
        - Bec pointu
        - Queue évasée
        - Pattes avec serres
        
        Returns: (positions, segment_ids, local_coords)
        """
        
        # === DIMENSIONS ===
        WINGSPAN = 140.0          # Envergure totale
        BODY_LENGTH = 35.0        # Longueur corps
        BODY_WIDTH = 12.0         # Largeur corps
        HEAD_RADIUS = 8.0         # Rayon tête
        HEAD_Y = 28.0             # Position Y tête
        TAIL_LENGTH = 25.0        # Longueur queue
        
        # === RÉPARTITION DRONES ===
        n_body = int(num * 0.12)
        n_wings = int(num * 0.55)  # 55% pour les ailes (détail important)
        n_head = int(num * 0.10)
        n_beak = int(num * 0.03)
        n_tail = int(num * 0.12)
        n_legs = int(num * 0.08)
        
        # Ajuster pour total exact
        total_assigned = n_body + n_wings + n_head + n_beak + n_tail + n_legs
        n_wings += (num - total_assigned)
        
        pos = np.zeros((num, 3))
        segment_ids = np.zeros(num, dtype=int)
        local_coords = np.zeros((num, 2))
        
        idx = 0
        CENTER_Y = 60.0  # Hauteur de base
        
        # === 1. CORPS (ellipsoïde) ===
        for i in range(n_body):
            if idx >= num:
                break
            # Distribution sur ellipsoïde
            u = np.random.uniform(0, 2 * np.pi)
            v = np.random.uniform(-1, 1)
            
            x = BODY_WIDTH * 0.5 * np.sqrt(1 - v*v) * np.cos(u)
            y = BODY_LENGTH * 0.5 * v
            z = BODY_WIDTH * 0.3 * np.sqrt(1 - v*v) * np.sin(u)
            
            pos[idx] = [x, y + CENTER_Y, z]
            segment_ids[idx] = 0
            local_coords[idx] = [x, y]
            idx += 1
        
        # === 2. AILES (avec détails de plumes) ===
        n_per_wing = n_wings // 2
        
        for wing_side in [-1, 1]:  # Gauche (-1) et Droite (+1)
            seg_id = 1 if wing_side < 0 else 2
            
            # Structure de l'aile: plusieurs couches de plumes
            # Primaires (extrémité), Secondaires (milieu), Tertiaires (proche corps)
            
            for i in range(n_per_wing):
                if idx >= num:
                    break
                
                # Paramétrage le long de l'aile
                t_along = i / n_per_wing  # 0 = corps, 1 = extrémité
                
                # Position X (distance du corps)
                x_base = 10 + t_along * 60  # De 10 à 70
                x = wing_side * x_base
                
                # Profil de l'aile (forme courbe)
                # Bord d'attaque (haut) et bord de fuite (bas)
                wing_chord = 25 * (1 - t_along * 0.6)  # Corde diminue vers l'extrémité
                
                # Position Y dans la corde de l'aile
                y_in_chord = np.random.uniform(-0.3, 0.7)  # Plus de drones vers le haut
                y_offset = y_in_chord * wing_chord
                
                # Courbure naturelle de l'aile
                curve = -5 * t_along * t_along  # Légèrement incurvée vers le bas
                
                y = CENTER_Y + y_offset + curve
                
                # Profondeur Z pour volume
                z = np.random.uniform(-3, 3) * (1 - t_along * 0.5)
                
                # Détail plumes: ondulation sur le bord de fuite
                if y_in_chord < -0.1:  # Bord de fuite (plumes visibles)
                    # Créer des "dents" pour les plumes primaires
                    feather_phase = x_base * 0.15
                    feather_wave = 3 * np.sin(feather_phase)
                    y += feather_wave * (1 - t_along)
                
                pos[idx] = [x, y, z]
                segment_ids[idx] = seg_id
                local_coords[idx] = [x, y - CENTER_Y]
                idx += 1
        
        # === 3. TÊTE (sphère + collerette) ===
        for i in range(n_head):
            if idx >= num:
                break
            
            # Distribution sur sphère
            u = np.random.uniform(0, 2 * np.pi)
            v = np.random.uniform(-0.3, 1)  # Plus de drones vers le haut/avant
            
            r = HEAD_RADIUS * (0.8 + 0.2 * np.random.random())  # Légère variation
            
            x = r * np.sqrt(1 - v*v) * np.cos(u) * 0.9
            y = r * v
            z = r * np.sqrt(1 - v*v) * np.sin(u) * 0.7
            
            # Collerette (plumes autour du cou) - élargir la base
            if y < -HEAD_RADIUS * 0.3:
                collar_expand = 1.3
                x *= collar_expand
                z *= collar_expand
            
            pos[idx] = [x, y + HEAD_Y + CENTER_Y, z]
            segment_ids[idx] = 3
            local_coords[idx] = [x, y + HEAD_Y]
            idx += 1
        
        # === 4. BEC ===
        for i in range(n_beak):
            if idx >= num:
                break
            
            # Bec pointu vers l'avant
            t_beak = i / max(1, n_beak - 1)
            
            x = 8 + t_beak * 6  # Pointe vers l'avant
            y = HEAD_Y + CENTER_Y - 2 - t_beak * 3  # Légèrement incliné vers le bas
            z = np.random.uniform(-1, 1) * (1 - t_beak)  # Plus fin vers la pointe
            
            pos[idx] = [x, y, z]
            segment_ids[idx] = 4
            local_coords[idx] = [x, y - CENTER_Y]
            idx += 1
        
        # === 5. QUEUE (éventail) ===
        for i in range(n_tail):
            if idx >= num:
                break
            
            # Distribution en éventail
            angle = np.random.uniform(-0.6, 0.6)  # Angle d'éventail
            t_tail = np.random.uniform(0, 1)  # Distance du corps
            
            x = np.sin(angle) * TAIL_LENGTH * t_tail
            y = CENTER_Y - 20 - np.cos(angle) * TAIL_LENGTH * t_tail
            z = np.random.uniform(-2, 2)
            
            # Structure des plumes de queue
            feather_idx = int(abs(angle) / 0.15)
            if t_tail > 0.7:  # Extrémité des plumes
                y -= 2 * np.sin(feather_idx * 1.5)
            
            pos[idx] = [x, y, z]
            segment_ids[idx] = 5
            local_coords[idx] = [x, y - CENTER_Y]
            idx += 1
        
        # === 6. PATTES ET SERRES ===
        for i in range(n_legs):
            if idx >= num:
                break
            
            # Deux pattes, chacune avec serres
            leg_side = 1 if i < n_legs // 2 else -1
            leg_idx = i % (n_legs // 2)
            t_leg = leg_idx / max(1, n_legs // 2 - 1)
            
            # Jambe principale
            if t_leg < 0.5:
                # Partie haute (cuisse)
                x = leg_side * 4
                y = CENTER_Y - 15 - t_leg * 20
                z = 3 + t_leg * 5
            else:
                # Serres (3 doigts en avant, 1 en arrière)
                claw_t = (t_leg - 0.5) * 2
                claw_idx = int(claw_t * 4) % 4
                
                base_x = leg_side * 4
                base_y = CENTER_Y - 35
                
                if claw_idx < 3:  # Doigts avant
                    angle = (claw_idx - 1) * 0.4
                    x = base_x + np.sin(angle) * 5 * claw_t
                    y = base_y - 3 * claw_t
                    z = 8 + np.cos(angle) * 3 * claw_t
                else:  # Doigt arrière
                    x = base_x
                    y = base_y - 2 * claw_t
                    z = 8 - 4 * claw_t
            
            pos[idx] = [x, y, z]
            segment_ids[idx] = 6
            local_coords[idx] = [x, y - CENTER_Y]
            idx += 1
        
        return pos, segment_ids, local_coords

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

        pos, cols = self._fill_shape_uniformly(is_in_mosque, (-60, 60, 0, 110), num, center=(0, 20, 0), z_depth=15.0)
        # Apply Miroir Céleste Colors (Gold/Orange mix)
        cols = np.tile(self.colors["soleil_or"], (num, 1))
        # Random mix with orange for a "living" building look
        orange_indices = np.random.rand(num) > 0.8
        cols[orange_indices] = self.colors["orange_niger"]
        return pos, cols

    def _phase_10_touareg(self, num, t=0.0):
        """
        � DROMADAIRE LUMINEUX EN MARCHE – SPÉCIFICATION COMPLÈTE
        
        ═══════════════════════════════════════════════════════════════
        IDENTIFICATION: DROMADAIRE (1 bosse unique) – profil latéral
        ═══════════════════════════════════════════════════════════════
        
        📋 RÉPARTITION OPTIMISÉE:
        ─────────────────────────
        • Contour principal : 40% des drones
        • Remplissage intérieur : 40% des drones  
        • Points clés (œil, museau, articulations) : 20% des drones
        
        🔬 PROPORTIONS ANATOMIQUES:
        ───────────────────────────
        • Hauteur totale ≈ 5-6× hauteur des pattes
        • Longueur corps ≈ 2× hauteur au garrot
        • Bosse haute, centrée sur le dos
        • Cou long et gracieusement arqué
        • Tête petite, museau allongé
        
        🔄 ANIMATION 4 PHASES (cycle = 2.0s):
        ─────────────────────────────────────
        Phase 1 (0-0.5s): Patte avant droite avance, arrière-gauche poussée
        Phase 2 (0.5-1s): Transfert poids, soulèvement avant gauche
        Phase 3 (1-1.5s): Patte arrière gauche avance, avant-gauche levé
        Phase 4 (1.5-2s): Retour position neutre
        
        🎨 PALETTE COULEURS:
        ────────────────────
        • Corps principal: Blanc pur (6000K)
        • Zones inférieures: Dégradé → orange chaud (3500K)
        • Contours: Bleu froid (7000K) accent
        • Points clés: Blanc intense + bloom
        
        💡 MOUVEMENTS SECONDAIRES:
        ──────────────────────────
        • Bosse: oscillation verticale ±3°
        • Cou: ondulation horizontale
        • Queue: balancement à contre-temps
        • Tête: hochement rythmique
        
        Dimensions: ~150m (L) × 90m (H)
        ═══════════════════════════════════════════════════════════════
        """

        # === CONSTRUCTION DU MESH (UNE SEULE FOIS) ===
        if num not in self._phase10_cache:
            rng = np.random.default_rng(42 + num)
            from scipy.interpolate import splprep, splev
            from matplotlib.path import Path

            # ════════════════════════════════════════════════════════════
            # 1. CONTOUR MAÎTRE SVG – 120+ points de contrôle
            # ════════════════════════════════════════════════════════════
            # Profil strict, sens horaire depuis queue
            # Échelle: ~140m × 80m
            
            raw_contour = np.array([
                # ─── QUEUE (fine, courbée vers le haut) ───
                [-68, 48], [-66, 52], [-64, 54], [-61, 53], [-58, 50], [-55, 47],
                
                # ─── CROUPE (descendante vers bosse) ───
                [-52, 44], [-48, 41], [-44, 38], [-40, 36], [-36, 35],
                
                # ─── BOSSE UNIQUE (dromadaire = 1 bosse haute et marquée) ───
                [-30, 36], [-24, 40], [-18, 46], [-12, 54], [-6, 60],
                [0, 64], [6, 66],  # Sommet de la bosse
                [12, 64], [18, 58], [24, 50], [28, 44],
                
                # ─── DOS vers ENCOLURE ───
                [32, 42], [36, 42],
                
                # ─── ENCOLURE (longue, courbure élégante) ───
                [40, 44], [44, 50], [48, 58], [52, 66], [56, 74], [58, 80],
                
                # ─── TÊTE (profil caractéristique avec chanfrein) ───
                [60, 84], [64, 86], [68, 85], [72, 82],  # Crâne arrondi
                [75, 78], [78, 74],  # Front
                [80, 70], [82, 66],  # Chanfrein (ligne du nez)
                [84, 62], [85, 58],  # Nez/museau
                [84, 54], [82, 51],  # Lèvre supérieure
                [79, 49], [76, 48], [73, 49],  # Menton
                
                # ─── GORGE (descente vers poitrail) ───
                [70, 52], [66, 56], [62, 60], [58, 62],
                [54, 62], [50, 58], [46, 52], [42, 46],
                
                # ─── POITRAIL ───
                [40, 42], [38, 36], [36, 30],
                
                # ═══ PATTE AVANT DROITE (FR) – bien séparée ═══
                [35, 26], [34, 20], [33, 14], [32, 8], [31, 2], [30, -2],
                [28, -2], [27, 0],  # Sabot FR
                [26, 6], [25, 14], [24, 22], [23, 28],
                
                # ─── ESPACE ENTRE PATTES AVANT (ventre visible) ───
                [20, 30], [17, 30], [14, 30],
                
                # ═══ PATTE AVANT GAUCHE (FL) ═══
                [12, 28], [11, 22], [10, 14], [9, 6], [8, 0], [7, -2],
                [5, -2], [4, 0],  # Sabot FL
                [3, 8], [2, 16], [1, 24],
                
                # ─── VENTRE (ligne basse) ───
                [-2, 26], [-8, 24], [-14, 22], [-20, 20], [-26, 18],
                
                # ═══ PATTE ARRIÈRE DROITE (RR) ═══
                [-30, 18], [-31, 12], [-32, 6], [-33, 0], [-34, -2],
                [-36, -2], [-37, 0],  # Sabot RR
                [-38, 8], [-39, 16], [-40, 24],
                
                # ─── ESPACE ENTRE PATTES ARRIÈRE ───
                [-43, 26], [-46, 26], [-49, 26],
                
                # ═══ PATTE ARRIÈRE GAUCHE (RL) ═══
                [-52, 24], [-53, 18], [-54, 10], [-55, 4], [-56, -2],
                [-58, -2], [-59, 2],  # Sabot RL
                [-60, 10], [-61, 20], [-62, 30],
                
                # ─── REMONTÉE VERS QUEUE ───
                [-64, 36], [-66, 42], [-68, 48],
            ], dtype=float)

            # B-spline lissage → 600 points haute définition
            try:
                tck, _ = splprep([raw_contour[:, 0], raw_contour[:, 1]], s=2.0, per=True, k=3)
                u_hd = np.linspace(0, 1, 600)
                contour_smooth = np.column_stack(splev(u_hd, tck))
            except Exception:
                contour_smooth = raw_contour.copy()

            # ════════════════════════════════════════════════════════════
            # 2. ÉCHANTILLONNAGE – RÉPARTITION OPTIMISÉE 40/40/20
            # ════════════════════════════════════════════════════════════
            n_contour = int(num * 0.40)   # 40% sur le contour
            n_interior = int(num * 0.40)  # 40% remplissage intérieur
            n_keypoints = num - n_contour - n_interior  # 20% points clés
            
            clen = len(contour_smooth)
            density = np.ones(clen)
            
            # Identifier les zones par position X approximative
            xs = contour_smooth[:, 0]
            ys = contour_smooth[:, 1]
            
            # Queue (×3)
            density[(xs < -60)] *= 3.0
            # Bosse (×2.5)
            density[(xs > -20) & (xs < 20) & (ys > 50)] *= 2.5
            # Tête/museau (×3)
            density[(xs > 70)] *= 3.0
            # Cou (×2)
            density[(xs > 50) & (xs < 70) & (ys > 60)] *= 2.0
            # Sabots/genoux (×3) - zones basses des pattes
            density[(ys < 10)] *= 3.0
            
            # Échantillonnage pondéré
            cumsum = np.cumsum(density)
            cumsum /= cumsum[-1]
            sample_u = np.linspace(0, 1, n_contour)
            idx_sample = np.searchsorted(cumsum, sample_u)
            idx_sample = np.clip(idx_sample, 0, clen - 1)
            pts_contour = contour_smooth[idx_sample].copy()

            # ════════════════════════════════════════════════════════════
            # 3. REMPLISSAGE POISSON-DISC CONTRAINT
            # ════════════════════════════════════════════════════════════
            poly_path = Path(contour_smooth)
            
            bx_min, bx_max = xs.min() - 2, xs.max() + 2
            by_min, by_max = ys.min() - 2, ys.max() + 2

            # Zones d'exclusion : espaces entre pattes = moins dense
            def exclusion_weight(x, y):
                """Retourne 0-1, 0 = exclure, 1 = garder"""
                w = 1.0
                # Entre pattes avant (x: 14-20, y < 32)
                if 14 < x < 20 and y < 32:
                    w *= 0.15
                # Entre pattes arrière (x: -49 à -43, y < 28)
                if -49 < x < -43 and y < 28:
                    w *= 0.15
                # Ventre central = léger
                if -26 < x < 0 and 18 < y < 28:
                    w *= 0.4
                return w

            # Génération Poisson-disc simplifiée avec rejection
            interior_pts = []
            batch = max(n_interior * 12, 10000)
            
            for _ in range(20):
                if len(interior_pts) >= n_interior:
                    break
                
                xs_rand = rng.uniform(bx_min, bx_max, batch)
                ys_rand = rng.uniform(by_min, by_max, batch)
                candidates = np.column_stack((xs_rand, ys_rand))
                
                inside_mask = poly_path.contains_points(candidates)
                valid = candidates[inside_mask]
                
                if len(valid) == 0:
                    continue
                
                # Appliquer pondération d'exclusion
                probs = np.array([exclusion_weight(p[0], p[1]) for p in valid])
                
                # Densité additionnelle : bosse et tête plus denses
                for i, p in enumerate(valid):
                    # Bosse
                    if -15 < p[0] < 15 and p[1] > 45:
                        probs[i] *= 1.8
                    # Tête
                    if p[0] > 60 and p[1] > 50:
                        probs[i] *= 1.6
                
                probs = np.clip(probs, 0.05, 1.0)
                accept = rng.random(len(valid)) < probs
                interior_pts.extend(valid[accept].tolist())
            
            interior_pts = np.array(interior_pts[:n_interior]) if len(interior_pts) >= n_interior else (
                np.array(interior_pts) if len(interior_pts) > 0 else np.zeros((0, 2))
            )

            # Compléter si nécessaire avec grille
            if len(interior_pts) < n_interior:
                needed = n_interior - len(interior_pts)
                res = int(np.sqrt(needed * 4)) + 10
                gx = np.linspace(bx_min, bx_max, res)
                gy = np.linspace(by_min, by_max, res)
                gxx, gyy = np.meshgrid(gx, gy)
                grid = np.column_stack((gxx.ravel(), gyy.ravel()))
                inside = poly_path.contains_points(grid)
                grid_valid = grid[inside]
                if len(grid_valid) >= needed:
                    pick = rng.choice(len(grid_valid), needed, replace=False)
                    extra = grid_valid[pick]
                else:
                    extra = grid_valid
                interior_pts = np.vstack([interior_pts, extra]) if len(interior_pts) > 0 else extra

            # ════════════════════════════════════════════════════════════
            # 4. ASSEMBLAGE + SEGMENTATION ANATOMIQUE
            # ════════════════════════════════════════════════════════════
            pts_contour += rng.normal(0, 0.3, pts_contour.shape)
            if len(interior_pts) > 0:
                interior_pts += rng.normal(0, 0.6, interior_pts.shape)

            all_2d = np.vstack([pts_contour, interior_pts]) if len(interior_pts) > 0 else pts_contour

            # Ajuster au nombre exact
            if len(all_2d) < num:
                shortage = num - len(all_2d)
                idx_dup = rng.choice(len(all_2d), shortage, replace=True)
                jitter = rng.normal(0, 0.5, (shortage, 2))
                all_2d = np.vstack([all_2d, all_2d[idx_dup] + jitter])
            elif len(all_2d) > num:
                all_2d = all_2d[:num]

            # 3D (profil strict)
            base_pos = np.zeros((num, 3))
            base_pos[:, 0] = all_2d[:, 0]
            base_pos[:, 1] = all_2d[:, 1] + 8  # Élever au-dessus du sol
            base_pos[:, 2] = rng.uniform(-1.5, 1.5, num)  # Faible profondeur

            # ═══════════════════════════════════════════════════════════
            # SEGMENTATION ANATOMIQUE STRICTE – ZONES X ABSOLUES
            # ═══════════════════════════════════════════════════════════
            # Basé sur le contour SVG réel:
            # - Pattes avant FR: X ~ 23-36 (contour original)
            # - Pattes avant FL: X ~ 1-14
            # - Pattes arrière RR: X ~ -40 à -28
            # - Pattes arrière RL: X ~ -62 à -50
            
            px, py = base_pos[:, 0], base_pos[:, 1]
            
            # Ligne du ventre (sépare pattes du corps)
            BELLY_Y = 32  # Y en dessous duquel = pattes
            
            # ─── PATTES AVANT (côté droit, X positif) ───
            seg_leg_fr = (px >= 22) & (px <= 37) & (py < BELLY_Y)  # Patte avant droite
            seg_leg_fl = (px >= 0) & (px <= 15) & (py < BELLY_Y)   # Patte avant gauche
            
            # ─── PATTES ARRIÈRE (côté gauche, X négatif) ───
            seg_leg_rr = (px >= -42) & (px <= -27) & (py < BELLY_Y - 2)  # Patte arrière droite
            seg_leg_rl = (px >= -65) & (px <= -48) & (py < BELLY_Y)      # Patte arrière gauche
            
            # ─── TÊTE (extrémité droite, haute) ───
            seg_head = (px >= 70) & (py >= 55)
            
            # ─── COU (entre tête et épaule) ───
            seg_neck = (px >= 50) & (px < 70) & (py >= 50) & ~seg_head
            
            # ─── BOSSE (zone centrale haute) ───
            seg_hump = (px >= -20) & (px <= 25) & (py >= 62)
            
            # ─── QUEUE (extrémité gauche) ───
            seg_tail = (px <= -60) & (py >= 48)
            
            # ─── TORSE (tout le reste) ───
            seg_torso = ~(seg_head | seg_neck | seg_hump | seg_tail | 
                          seg_leg_fr | seg_leg_fl | seg_leg_rr | seg_leg_rl)
            
            # ─── Points de pivot pour animation (hanches au niveau BELLY_Y) ───
            pivots = {
                "hip_fr": np.array([29.5, BELLY_Y]),   # Centre de la zone FR
                "hip_fl": np.array([7.5, BELLY_Y]),    # Centre de la zone FL
                "hip_rr": np.array([-34.5, BELLY_Y - 2]),  # Centre de la zone RR
                "hip_rl": np.array([-56.5, BELLY_Y]),  # Centre de la zone RL
                "neck_base": np.array([42, 50]),
                "tail_base": np.array([-62, 50]),
                # Points d'articulation critiques pour bloom
                "shoulder": np.array([35, 34]),     # Épaule
                "knee_fr": np.array([31, 12]),      # Genou avant droit
                "knee_fl": np.array([8, 12]),       # Genou avant gauche
                "knee_rr": np.array([-35, 10]),     # Genou arrière droit
                "knee_rl": np.array([-57, 10]),     # Genou arrière gauche
                "eye": np.array([75, 78]),          # Œil
                "muzzle": np.array([85, 56]),       # Museau
            }
            
            # ─── Points clés (articulations + œil + museau) pour haute densité ───
            keypoint_centers = [
                pivots["shoulder"], pivots["hip_fr"], pivots["hip_fl"],
                pivots["hip_rr"], pivots["hip_rl"],
                pivots["knee_fr"], pivots["knee_fl"], pivots["knee_rr"], pivots["knee_rl"],
                pivots["eye"], pivots["muzzle"], pivots["neck_base"], pivots["tail_base"],
            ]
            
            # Marquer les drones proches des points clés
            keypoint_radius = 6.0
            is_keypoint = np.zeros(num, dtype=bool)
            for kp in keypoint_centers:
                dist = np.sqrt((px - kp[0])**2 + (py - kp[1] - 8)**2)  # -8 pour offset Y
                is_keypoint |= (dist < keypoint_radius)

            # ════════════════════════════════════════════════════════════
            # 5. PALETTE DE COULEURS ENRICHIE
            # ════════════════════════════════════════════════════════════
            # Corps principal : Blanc pur (6000K) → RGB(1.0, 1.0, 1.0)
            # Zones inférieures : Orange chaud (3500K) → RGB(1.0, 0.75, 0.45)
            # Contours : Bleu froid accent (7000K) → RGB(0.85, 0.92, 1.0)
            # Points clés : Blanc intense + bloom
            
            base_cols = np.zeros((num, 3))
            
            # ─── Contour: Bleu froid accent (7000K) pour silhouette nette ───
            cool_blue = np.array([0.88, 0.94, 1.0])
            base_cols[:n_contour] = cool_blue * 1.10
            
            # ─── Intérieur: Dégradé blanc pur → orange chaud ───
            if len(interior_pts) > 0:
                y_int = base_pos[n_contour:n_contour + len(interior_pts), 1]
                y_min, y_max = y_int.min(), max(y_int.max(), y_int.min() + 1)
                y_norm = (y_int - y_min) / (y_max - y_min)
                
                warm_orange = np.array([1.0, 0.75, 0.45])   # Bas: 3500K orange chaud
                pure_white = np.array([1.0, 1.0, 1.0])      # Haut: 6000K blanc pur
                
                blend = y_norm[:, None]
                base_cols[n_contour:n_contour + len(interior_pts)] = warm_orange * (1 - blend) + pure_white * blend
            
            # ─── Pattes: glow fort pour visibilité ───
            for seg in [seg_leg_fr, seg_leg_fl, seg_leg_rr, seg_leg_rl]:
                base_cols[seg] *= 1.12
            
            # ─── Points clés (articulations, œil, museau): Blanc intense + bloom ───
            intense_white = np.array([1.0, 1.0, 1.0])
            base_cols[is_keypoint] = intense_white * 1.25  # Surbrillance bloom
            
            # ─── Bosse: Point focal brillant ───
            base_cols[seg_hump] = np.array([1.0, 0.98, 0.92]) * 1.15
            
            # ─── Tête et cou: Blanc pur légèrement accentué ───
            base_cols[seg_head] = np.array([1.0, 1.0, 0.98]) * 1.10
            base_cols[seg_neck] = np.array([1.0, 0.98, 0.95]) * 1.05
            
            base_cols = np.clip(base_cols, 0, 1)

            self._phase10_cache[num] = {
                "pos": base_pos.copy(),
                "cols": base_cols.copy(),
                "n_contour": n_contour,
                "seg_head": seg_head,
                "seg_neck": seg_neck,
                "seg_hump": seg_hump,
                "seg_tail": seg_tail,
                "seg_leg_fr": seg_leg_fr,
                "seg_leg_fl": seg_leg_fl,
                "seg_leg_rr": seg_leg_rr,
                "seg_leg_rl": seg_leg_rl,
                "seg_torso": seg_torso,
                "pivots": pivots,
                "is_keypoint": is_keypoint,  # Points clés pour bloom
            }

        # ════════════════════════════════════════════════════════════
        # ANIMATION MARCHE BIOMÉCANIQUE – GAIT LATÉRAL AUTHENTIQUE
        # ════════════════════════════════════════════════════════════
        cached = self._phase10_cache[num]
        animated = cached["pos"].copy()
        cols = cached["cols"].copy()
        n_contour = cached["n_contour"]
        pivots = cached["pivots"]

        # ═══════════════════════════════════════════════════════════
        # CYCLE DE MARCHE 4 PHASES (2.0 secondes = réaliste dromadaire)
        # ═══════════════════════════════════════════════════════════
        # Phase 1 (0-0.5s): Patte avant droite avance, arrière-gauche poussée
        # Phase 2 (0.5-1s): Transfert poids, soulèvement avant gauche
        # Phase 3 (1-1.5s): Patte arrière gauche avance, avant-gauche levé  
        # Phase 4 (1.5-2s): Retour position neutre
        
        CYCLE_DURATION = 2.0
        phi = (t % CYCLE_DURATION) / CYCLE_DURATION  # Phase normalisée 0→1
        
        # Identifier la phase actuelle (1-4)
        current_phase_num = int(phi * 4) + 1  # 1, 2, 3, ou 4
        phase_progress = (phi * 4) % 1.0      # Progression dans la phase (0→1)

        # ───────────────────────────────────────────────────────────
        # INTERPOLATION MINIMUM-JERK: s(t) = 10t³ - 15t⁴ + 6t⁵
        # → Accélération douce, zéro à-coup
        # ───────────────────────────────────────────────────────────
        def min_jerk(x):
            """Interpolation minimum-jerk pour mouvement naturel."""
            x = np.clip(x, 0, 1)
            return 10 * x**3 - 15 * x**4 + 6 * x**5

        # ───────────────────────────────────────────────────────────
        # TRAJECTOIRE DE PATTE (elliptique avec phase aérienne/sol)
        # ───────────────────────────────────────────────────────────
        def leg_trajectory(phase_offset, step_len=8.0, lift_height=6.0):
            """
            Calcule le déplacement X et élévation Z d'une patte.
            
            phase < 0.5 : Phase aérienne (levée + avancée)
            phase >= 0.5: Phase au sol (retour en arrière)
            
            Returns: (dx, dz) déplacements
            """
            local_phi = (phi + phase_offset) % 1.0
            
            if local_phi < 0.5:
                # Phase aérienne: avancée lente avec levée
                t_air = local_phi / 0.5  # 0→1 pendant phase aérienne
                t_smooth = min_jerk(t_air)
                dx = step_len * (t_smooth - 0.5)
                dz = lift_height * np.sin(np.pi * t_air)  # Arc sinusoïdal
            else:
                # Phase au sol: retour rapide
                t_ground = (local_phi - 0.5) / 0.5  # 0→1 pendant phase sol
                t_smooth = min_jerk(t_ground)
                dx = step_len * (0.5 - t_smooth)
                dz = 0.0  # Patte au sol
            
            return dx, dz

        # ═══════════════════════════════════════════════════════════
        # GAIT LATÉRAL (AMBLE) – CHAMEAU AUTHENTIQUE
        # ═══════════════════════════════════════════════════════════
        # FL + RL ensemble (côté gauche)
        # FR + RR ensemble (côté droit), déphasé de 0.5
        
        PHASE_LEFT = 0.0    # Côté gauche: phase 0
        PHASE_RIGHT = 0.5   # Côté droit: phase 0.5

        def animate_leg(mask, pivot, phase_offset, step_len=8.0, lift_height=6.0, swing_amp=0.20):
            """
            Anime une patte avec:
            - Rotation autour de la hanche (swing)
            - Translation avant/arrière (step)
            - Élévation pendant phase aérienne (lift)
            """
            if not np.any(mask):
                return
            
            # Calculer trajectoire
            dx_step, dz_lift = leg_trajectory(phase_offset, step_len, lift_height)
            
            # Phase locale pour swing
            local_phi = (phi + phase_offset) % 1.0
            swing_angle = swing_amp * np.sin(2 * np.pi * local_phi)
            
            # Rotation autour de la hanche
            cos_a, sin_a = np.cos(swing_angle), np.sin(swing_angle)
            rel_x = animated[mask, 0] - pivot[0]
            rel_y = animated[mask, 1] - pivot[1]
            
            # Appliquer rotation
            new_x = pivot[0] + rel_x * cos_a - rel_y * sin_a
            new_y = pivot[1] + rel_x * sin_a + rel_y * cos_a
            
            animated[mask, 0] = new_x
            animated[mask, 1] = new_y
            
            # Appliquer élévation (plus forte au sabot qu'à la cuisse)
            dist_from_hip = np.sqrt(rel_x**2 + rel_y**2)
            lift_factor = np.clip(dist_from_hip / 25.0, 0.2, 1.0)
            animated[mask, 1] += dz_lift * lift_factor

        # ─── Animer les 4 pattes ───
        # Côté gauche (FL + RL) ensemble
        animate_leg(cached["seg_leg_fl"], pivots["hip_fl"], PHASE_LEFT, step_len=7.0, lift_height=5.5, swing_amp=0.18)
        animate_leg(cached["seg_leg_rl"], pivots["hip_rl"], PHASE_LEFT, step_len=6.5, lift_height=5.0, swing_amp=0.16)
        
        # Côté droit (FR + RR) ensemble, déphasé de 0.5
        animate_leg(cached["seg_leg_fr"], pivots["hip_fr"], PHASE_RIGHT, step_len=7.0, lift_height=5.5, swing_amp=0.18)
        animate_leg(cached["seg_leg_rr"], pivots["hip_rr"], PHASE_RIGHT, step_len=6.5, lift_height=5.0, swing_amp=0.16)

        # ═══════════════════════════════════════════════════════════
        # MOUVEMENTS SECONDAIRES – TRONC ET BOSSE
        # ═══════════════════════════════════════════════════════════
        torso_mask = cached["seg_torso"]
        hump_mask = cached["seg_hump"]
        body_mask = torso_mask | hump_mask
        
        # ─── Body sway (oscillation latérale Z, synchronisée avec pas) ───
        body_sway = 0.03 * np.sin(4 * np.pi * phi)  # ±3% en Z
        animated[body_mask, 2] += body_sway * 40  # Échelle monde
        
        # ─── Body bob (oscillation verticale, 2× par cycle car 2 pas) ───
        body_bob = 0.02 * np.sin(4 * np.pi * phi)  # ±2% en Y
        animated[body_mask, 1] += body_bob * 50
        
        # ─── Légère inclinaison vers l'avant (dynamique de marche) ───
        # Le buste s'incline légèrement selon la phase
        tilt_forward = 0.015 * np.sin(2 * np.pi * phi)  # ±1.5%
        
        # ─── BOSSE : Oscillation verticale ±3° + inertie retardée ───
        hump_oscillation = np.radians(3.0) * np.sin(4 * np.pi * phi)  # ±3 degrés
        hump_lag = 0.5 * body_sway  # Inertie retardée
        
        if np.any(hump_mask):
            # Oscillation verticale de la bosse
            hump_center_y = 70  # Centre Y approximatif de la bosse
            rel_y = animated[hump_mask, 1] - hump_center_y
            animated[hump_mask, 1] += hump_oscillation * np.abs(rel_y) * 0.15
            # Retard d'inertie latérale
            animated[hump_mask, 2] += hump_lag * 25

        # ═══════════════════════════════════════════════════════════
        # TÊTE ET COU – HOCHEMENT RYTHMIQUE + ONDULATION HORIZONTALE
        # ═══════════════════════════════════════════════════════════
        head_mask = cached["seg_head"]
        neck_mask = cached["seg_neck"]
        neck_base = pivots["neck_base"]
        
        # ─── Hochement vertical (synchronisé avec pas, léger retard) ───
        head_phase = phi - 0.1  # Retard de 10% du cycle
        head_bob = 3.0 * np.sin(4 * np.pi * head_phase)  # Amplitude augmentée
        
        if np.any(head_mask):
            # Tête haute pendant poussée, basse pendant levée
            animated[head_mask, 1] += head_bob * 1.2
        if np.any(neck_mask):
            # Cou: gradient de mouvement (base moins, sommet plus)
            neck_y = animated[neck_mask, 1]
            neck_gradient = np.clip((neck_y - neck_base[1]) / 30.0, 0.3, 1.0)
            animated[neck_mask, 1] += head_bob * 0.6 * neck_gradient
        
        # ─── Ondulation horizontale du cou (mouvement en S) ───
        neck_wave_phase = phi * 2 * np.pi + 0.3
        neck_wave_amp = 2.5  # Amplitude de l'ondulation
        
        if np.any(neck_mask):
            neck_y = animated[neck_mask, 1]
            neck_height_factor = np.clip((neck_y - neck_base[1]) / 35.0, 0, 1)
            neck_wave = neck_wave_amp * np.sin(neck_wave_phase) * neck_height_factor
            animated[neck_mask, 2] += neck_wave
        
        # ─── Balancement latéral de la tête (en Z) ───
        head_sway = 2.2 * np.sin(2 * np.pi * phi + 0.25)
        if np.any(head_mask):
            animated[head_mask, 2] += head_sway
        if np.any(neck_mask):
            animated[neck_mask, 2] += head_sway * 0.35

        # ═══════════════════════════════════════════════════════════
        # QUEUE – BALANCEMENT À CONTRE-TEMPS NATUREL
        # ═══════════════════════════════════════════════════════════
        tail_mask = cached["seg_tail"]
        tail_base = pivots["tail_base"]
        
        if np.any(tail_mask):
            # ─── Phase à contre-temps des pattes (opposition naturelle) ───
            # Quand pattes gauches avancent → queue va à droite, et inversement
            tail_phase = phi + 0.5 + 0.25  # À contre-temps + décalage
            
            # ─── Rotation principale autour de la base ───
            tail_swing_amp = 0.15  # ±8.5 degrés
            tail_angle = tail_swing_amp * np.sin(2 * np.pi * tail_phase)
            cos_t, sin_t = np.cos(tail_angle), np.sin(tail_angle)
            
            dx = animated[tail_mask, 0] - tail_base[0]
            dy = animated[tail_mask, 1] - tail_base[1]
            
            animated[tail_mask, 0] = tail_base[0] + dx * cos_t - dy * sin_t
            animated[tail_mask, 1] = tail_base[1] + dx * sin_t + dy * cos_t
            
            # ─── Ondulation latérale (mouvement de fouet en Z) ───
            # Plus grande amplitude à l'extrémité qu'à la base
            dist_from_base = np.sqrt(dx**2 + dy**2)
            wave_factor = np.clip(dist_from_base / 10.0, 0.3, 1.0)
            tail_wave = 3.5 * np.sin(4 * np.pi * tail_phase - 0.7) * wave_factor
            animated[tail_mask, 2] += tail_wave
            
            # ─── Micro-oscillation secondaire (queue "vivante") ───
            tail_micro = 0.8 * np.sin(8 * np.pi * phi + dist_from_base * 0.3)
            animated[tail_mask, 2] += tail_micro

        # ═══════════════════════════════════════════════════════════
        # EFFETS DYNAMIQUES – BLOOM + PULSATION SYNCHRONISÉE
        # ═══════════════════════════════════════════════════════════
        
        # ─── Contour: Bleu froid avec glow pulsé synchronisé ───
        # Pulsation liée au rythme de marche (2× par cycle)
        glow_pulse = 0.90 + 0.10 * np.sin(4 * np.pi * phi)
        cols[:n_contour] *= glow_pulse
        
        # ─── Pattes: Bloom augmenté pendant phase de levée ───
        for seg, phase_offset in [(cached["seg_leg_fl"], PHASE_LEFT),
                                   (cached["seg_leg_rl"], PHASE_LEFT),
                                   (cached["seg_leg_fr"], PHASE_RIGHT),
                                   (cached["seg_leg_rr"], PHASE_RIGHT)]:
            if np.any(seg):
                local_phi = (phi + phase_offset) % 1.0
                # Bloom plus fort pendant phase aérienne (levée)
                if local_phi < 0.5:
                    leg_bloom = 1.08 + 0.12 * np.sin(np.pi * local_phi / 0.5)
                else:
                    leg_bloom = 1.05
                cols[seg] *= leg_bloom
        
        # ─── Articulations (genoux, hanches): Bloom intense ───
        # Utiliser is_keypoint du cache
        is_keypoint = cached.get("is_keypoint", np.zeros(num, dtype=bool))
        if np.any(is_keypoint):
            articulation_bloom = 1.15 + 0.10 * np.sin(4 * np.pi * phi + 0.5)
            cols[is_keypoint] *= articulation_bloom
        
        # ─── Bosse: Point focal avec pulsation lente ───
        if np.any(hump_mask):
            hump_glow = 1.10 + 0.08 * np.sin(2 * np.pi * phi)
            cols[hump_mask] *= hump_glow
        
        # ─── Tête: Micro-scintillement + œil brillant ───
        if np.any(head_mask):
            n_head = np.sum(head_mask)
            head_sparkle = 0.95 + 0.08 * np.sin(t * 1.2 + np.arange(n_head) * 0.12)
            cols[head_mask] *= head_sparkle[:, None]
        
        # ─── Queue: Traînée lumineuse (plus brillant à l'extrémité) ───
        if np.any(tail_mask):
            tail_x = animated[tail_mask, 0]
            trail_factor = np.clip((tail_base[0] - tail_x) / 8.0, 0.8, 1.3)
            cols[tail_mask] *= trail_factor[:, None]
        
        # Clip final
        cols = np.clip(cols, 0, 1)

        # Légère ondulation Z pour effet vivant (synchronisée avec le cycle)
        idx = np.arange(num)
        animated[:, 2] += 0.3 * np.sin(0.15 * idx + 2 * np.pi * phi)

        return animated, cols

    def _phase_dubai_camel(self, num, t=0.0):
        """
        🐫 CHAMEAU DE DUBAÏ – STYLE MINIMALISTE WORLD RECORD
        
        ═══════════════════════════════════════════════════════════════
        SPÉCIFICATION: Dubai Drone Show Guinness World Record Style
        ═══════════════════════════════════════════════════════════════
        
        🎯 CARACTÉRISTIQUES CLÉS:
        ─────────────────────────
        • DEUX BOSSES (Chameau Bactrien) symétriques
        • Style ÉPURÉ minimaliste – contours uniquement
        • Pas de remplissage dense – silhouette pure
        • Blanc pur #FFFFFF sur fond noir
        • Échelle MONUMENTALE
        
        📐 PROPORTIONS:
        ───────────────
        • Largeur totale: ~100m
        • Hauteur totale: ~50m
        • Contour principal: 95% des drones
        • Marche lente majestueuse (cycle 4s)
        
        🎨 ÉCLAIRAGE:
        ─────────────
        • Couleur: Blanc pur uniforme
        • Intensité: Maximale (100%)
        • Bloom léger sur contour
        • Aucun effet spécial (minimalisme)
        
        Dimensions: ~100m (L) × 50m (H)
        ═══════════════════════════════════════════════════════════════
        """
        
        cache_key = f"dubai_camel_{num}"
        
        if cache_key not in self._phase10_cache:
            rng = np.random.default_rng(1001 + num)
            from scipy.interpolate import splprep, splev
            
            # ════════════════════════════════════════════════════════════
            # CONTOUR MINIMALISTE – CHAMEAU À DEUX BOSSES (BACTRIEN)
            # ════════════════════════════════════════════════════════════
            # Style épuré Dubai Drone Show – courbes douces, géométrie simple
            # Échelle: 100m × 50m
            
            raw_contour = np.array([
                # ─── QUEUE (courte, simple) ───
                [-48, 22], [-46, 25], [-44, 26],
                
                # ─── CROUPE (montée vers bosse arrière) ───
                [-40, 27], [-36, 30], [-32, 35],
                
                # ═══ BOSSE ARRIÈRE (demi-cercle symétrique) ═══
                [-28, 42], [-24, 48], [-20, 52], [-16, 54],  # Montée
                [-12, 54], [-8, 52], [-4, 48],               # Sommet
                [0, 42],                                      # Descente
                
                # ─── SELLE (creux entre les bosses) ───
                [4, 38], [8, 36], [12, 38],
                
                # ═══ BOSSE AVANT (demi-cercle symétrique) ═══
                [16, 42], [20, 48], [24, 52], [28, 54],      # Montée
                [32, 54], [36, 52], [40, 48],                # Sommet
                [44, 42],                                     # Descente
                
                # ─── ENCOLURE (courbe douce vers tête) ───
                [48, 40], [52, 42], [56, 48], [60, 56], [64, 64],
                
                # ─── TÊTE (triangulaire allongée stylisée) ───
                [68, 68], [72, 70], [76, 68],   # Crâne
                [80, 64], [82, 58],             # Front/chanfrein
                [84, 52], [82, 48],             # Museau
                [78, 46], [74, 48],             # Menton
                
                # ─── GORGE (descente vers poitrail) ───
                [70, 50], [66, 52], [62, 52], [58, 48],
                [54, 42], [50, 36], [48, 30],
                
                # ═══ PATTE AVANT DROITE (rectangle étroit) ═══
                [46, 26], [45, 18], [44, 10], [43, 2],
                [41, 2], [40, 10], [39, 18], [38, 24],
                
                # ─── ESPACE AVANT ───
                [34, 24], [30, 24],
                
                # ═══ PATTE AVANT GAUCHE (rectangle étroit) ═══
                [28, 24], [27, 16], [26, 8], [25, 2],
                [23, 2], [22, 8], [21, 16], [20, 22],
                
                # ─── VENTRE (ligne simple) ───
                [16, 22], [8, 20], [0, 18], [-8, 18], [-16, 20],
                
                # ═══ PATTE ARRIÈRE DROITE (rectangle étroit) ═══
                [-20, 20], [-21, 12], [-22, 4], [-23, -2],
                [-25, -2], [-26, 4], [-27, 12], [-28, 18],
                
                # ─── ESPACE ARRIÈRE ───
                [-32, 18], [-36, 18],
                
                # ═══ PATTE ARRIÈRE GAUCHE (rectangle étroit) ═══
                [-38, 18], [-39, 10], [-40, 4], [-41, -2],
                [-43, -2], [-44, 4], [-45, 12], [-46, 20],
                
                # ─── RETOUR VERS QUEUE ───
                [-48, 22],
            ], dtype=float)
            
            # B-spline lissage pour courbes douces (style Dubai)
            try:
                tck, _ = splprep([raw_contour[:, 0], raw_contour[:, 1]], s=3.0, per=True, k=3)
                u_hd = np.linspace(0, 1, num)  # Tous les drones sur le contour
                contour_smooth = np.column_stack(splev(u_hd, tck))
            except Exception:
                # Fallback: répéter le contour brut
                repeat = max(1, num // len(raw_contour) + 1)
                contour_smooth = np.tile(raw_contour, (repeat, 1))[:num]
            
            # ════════════════════════════════════════════════════════════
            # POSITIONNEMENT 3D – CONTOURS UNIQUEMENT (MINIMALISTE)
            # ════════════════════════════════════════════════════════════
            pts_2d = contour_smooth[:num].copy()
            
            # Ajuster au nombre exact
            if len(pts_2d) < num:
                shortage = num - len(pts_2d)
                idx_dup = rng.choice(len(pts_2d), shortage, replace=True)
                jitter = rng.normal(0, 0.2, (shortage, 2))
                pts_2d = np.vstack([pts_2d, pts_2d[idx_dup] + jitter])
            
            # Petit jitter pour éviter superposition parfaite
            pts_2d += rng.normal(0, 0.15, pts_2d.shape)
            
            # 3D: profil plat (2D sur plan XY)
            base_pos = np.zeros((num, 3))
            base_pos[:, 0] = pts_2d[:, 0]
            base_pos[:, 1] = pts_2d[:, 1] + 20  # Élever au-dessus du sol
            base_pos[:, 2] = rng.uniform(-0.5, 0.5, num)  # Très faible profondeur
            
            # ════════════════════════════════════════════════════════════
            # SEGMENTATION SIMPLIFIÉE
            # ════════════════════════════════════════════════════════════
            px, py = base_pos[:, 0], base_pos[:, 1]
            BELLY_Y = 26 + 20  # Ligne du ventre ajustée
            
            # Pattes (zones X pour animation)
            seg_leg_fr = (px >= 38) & (px <= 48) & (py < BELLY_Y)
            seg_leg_fl = (px >= 20) & (px <= 30) & (py < BELLY_Y)
            seg_leg_rr = (px >= -28) & (px <= -18) & (py < BELLY_Y)
            seg_leg_rl = (px >= -48) & (px <= -36) & (py < BELLY_Y)
            
            # Tête
            seg_head = (px >= 68) & (py >= 60)
            
            # Cou
            seg_neck = (px >= 54) & (px < 68) & (py >= 48)
            
            # Bosses
            seg_hump_front = (px >= 12) & (px <= 48) & (py >= 58)
            seg_hump_rear = (px >= -28) & (px <= 4) & (py >= 56)
            seg_humps = seg_hump_front | seg_hump_rear
            
            # Queue
            seg_tail = (px <= -44) & (py >= 42)
            
            # Torse (reste)
            seg_torso = ~(seg_head | seg_neck | seg_humps | seg_tail |
                          seg_leg_fr | seg_leg_fl | seg_leg_rr | seg_leg_rl)
            
            # Pivots pour animation
            pivots = {
                "hip_fr": np.array([43, BELLY_Y]),
                "hip_fl": np.array([25, BELLY_Y]),
                "hip_rr": np.array([-23, BELLY_Y]),
                "hip_rl": np.array([-42, BELLY_Y]),
                "neck_base": np.array([50, 56]),
                "tail_base": np.array([-46, 44]),
            }
            
            # ════════════════════════════════════════════════════════════
            # COULEURS – BLANC PUR UNIFORME (STYLE DUBAI)
            # ════════════════════════════════════════════════════════════
            base_cols = np.ones((num, 3))  # Blanc pur #FFFFFF
            
            self._phase10_cache[cache_key] = {
                "pos": base_pos.copy(),
                "cols": base_cols.copy(),
                "seg_head": seg_head,
                "seg_neck": seg_neck,
                "seg_humps": seg_humps,
                "seg_tail": seg_tail,
                "seg_leg_fr": seg_leg_fr,
                "seg_leg_fl": seg_leg_fl,
                "seg_leg_rr": seg_leg_rr,
                "seg_leg_rl": seg_leg_rl,
                "seg_torso": seg_torso,
                "pivots": pivots,
            }
        
        # ════════════════════════════════════════════════════════════
        # ANIMATION MARCHE MAJESTUEUSE (CYCLE LENT 4.0s)
        # ════════════════════════════════════════════════════════════
        cached = self._phase10_cache[cache_key]
        animated = cached["pos"].copy()
        cols = cached["cols"].copy()
        pivots = cached["pivots"]
        
        # Cycle de marche lent et majestueux (4 secondes)
        CYCLE_DURATION = 4.0
        phi = (t % CYCLE_DURATION) / CYCLE_DURATION
        
        # Interpolation minimum-jerk pour fluidité
        def min_jerk(x):
            x = np.clip(x, 0, 1)
            return 10 * x**3 - 15 * x**4 + 6 * x**5
        
        # Trajectoire de patte simplifiée
        def leg_trajectory(phase_offset, step_len=4.0, lift_height=3.0):
            local_phi = (phi + phase_offset) % 1.0
            
            if local_phi < 0.5:
                t_air = local_phi / 0.5
                t_smooth = min_jerk(t_air)
                dx = step_len * (t_smooth - 0.5)
                dz = lift_height * np.sin(np.pi * t_air)
            else:
                t_ground = (local_phi - 0.5) / 0.5
                t_smooth = min_jerk(t_ground)
                dx = step_len * (0.5 - t_smooth)
                dz = 0.0
            
            return dx, dz
        
        # Phases de marche (opposées avant/arrière)
        PHASE_FR = 0.0
        PHASE_FL = 0.5
        PHASE_RR = 0.25
        PHASE_RL = 0.75
        
        def animate_leg(mask, pivot, phase_offset, step_len=4.0, lift_height=3.0, swing_amp=0.10):
            if not np.any(mask):
                return
            
            dx_step, dz_lift = leg_trajectory(phase_offset, step_len, lift_height)
            local_phi = (phi + phase_offset) % 1.0
            swing_angle = swing_amp * np.sin(2 * np.pi * local_phi)
            
            cos_a, sin_a = np.cos(swing_angle), np.sin(swing_angle)
            rel_x = animated[mask, 0] - pivot[0]
            rel_y = animated[mask, 1] - pivot[1]
            
            new_x = pivot[0] + rel_x * cos_a - rel_y * sin_a
            new_y = pivot[1] + rel_x * sin_a + rel_y * cos_a
            
            animated[mask, 0] = new_x
            animated[mask, 1] = new_y
            
            dist_from_hip = np.sqrt(rel_x**2 + rel_y**2)
            lift_factor = np.clip(dist_from_hip / 20.0, 0.2, 1.0)
            animated[mask, 1] += dz_lift * lift_factor
        
        # Animer les 4 pattes
        animate_leg(cached["seg_leg_fr"], pivots["hip_fr"], PHASE_FR, step_len=3.5, lift_height=2.5, swing_amp=0.08)
        animate_leg(cached["seg_leg_fl"], pivots["hip_fl"], PHASE_FL, step_len=3.5, lift_height=2.5, swing_amp=0.08)
        animate_leg(cached["seg_leg_rr"], pivots["hip_rr"], PHASE_RR, step_len=3.0, lift_height=2.0, swing_amp=0.07)
        animate_leg(cached["seg_leg_rl"], pivots["hip_rl"], PHASE_RL, step_len=3.0, lift_height=2.0, swing_amp=0.07)
        
        # ═══════════════════════════════════════════════════════════
        # MOUVEMENTS SECONDAIRES SUBTILS
        # ═══════════════════════════════════════════════════════════
        
        # Corps: légère oscillation verticale (body_sway = 0.05)
        body_mask = cached["seg_torso"] | cached["seg_humps"]
        body_bob = 0.05 * np.sin(4 * np.pi * phi) * 30  # ±1.5 unités
        animated[body_mask, 1] += body_bob
        
        # Tête: très léger hochement (head_movement = 0.03)
        head_mask = cached["seg_head"]
        neck_mask = cached["seg_neck"]
        head_phase = phi - 0.08
        head_bob = 0.03 * np.sin(4 * np.pi * head_phase) * 40
        
        if np.any(head_mask):
            animated[head_mask, 1] += head_bob
        if np.any(neck_mask):
            animated[neck_mask, 1] += head_bob * 0.4
        
        # Queue: presque immobile (très subtil)
        tail_mask = cached["seg_tail"]
        if np.any(tail_mask):
            tail_wave = 0.5 * np.sin(2 * np.pi * phi + 0.5)
            animated[tail_mask, 2] += tail_wave
        
        # ═══════════════════════════════════════════════════════════
        # ÉCLAIRAGE UNIFORME BLANC (MINIMALISME DUBAI)
        # ═══════════════════════════════════════════════════════════
        # Légère pulsation uniforme pour bloom
        glow_pulse = 0.95 + 0.05 * np.sin(t * 1.5)
        cols *= glow_pulse
        
        cols = np.clip(cols, 0, 1)
        
        return animated, cols

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
        return self._fill_shape_uniformly(is_in_croix, (-35*sc, 35*sc, -70*sc, 45*sc), num, center=(0, 75, -30.0), z_depth=10.0)

    def _phase_touareg_spiral(self, num, t=0.0, audio_energy=0.5):
        """
        Spirale Touareg Sacrale: Géométrie traditionnelle sahélienne.
        Morphe graduellement vers 22EMEEDITION après 3 secondes.
        Couleurs: Doré→Vert→Bleu (gradient sahélien).
        """
        
        # === PARAMETERS ===
        spiral_radius_outer = 60.0
        spiral_radius_inner = 10.0
        spiral_height = 80.0  # Z dimension for 3D spiral
        spiral_turns = 3.0    # Nombre de rotations
        
        # === ANIMATION ===
        # Phase 0-3s: Spiral full (entry)
        # Phase 3-5s: Morphing vers 22EMEEDITION (dissolve)
        if t < 3.0:
            morph_progress = 0.0  # No morphing yet
        elif t < 5.0:
            morph_progress = (t - 3.0) / 2.0  # Morph over 2 seconds
        else:
            morph_progress = 1.0  # Fully morphed (shouldn't see this)
        
        # === VOXEL GENERATION ===
        pos = np.zeros((num, 3))
        cols = np.zeros((num, 3))
        
        voxel_count = 0
        voxels = []
        voxel_colors = []
        
        # Generate spiral pattern
        angle_step = 2.0 * np.pi / (num // 4)  # Distribute drones around spiral
        
        for i in range(num):
            angle = (i / (num / (spiral_turns * 2.0 * np.pi))) + t * 0.5  # Rotating spiral
            
            # Spiral radius (from inner to outer)
            radius = spiral_radius_inner + (spiral_radius_outer - spiral_radius_inner) * (angle / (spiral_turns * 2.0 * np.pi))
            radius = np.clip(radius, spiral_radius_inner, spiral_radius_outer)
            
            # Position on spiral
            x = radius * np.cos(angle)
            z = radius * np.sin(angle)
            y = 50.0 + (angle / (spiral_turns * 2.0 * np.pi)) * spiral_height
            
            # Oscillation for organic motion
            oscillation = 3.0 * np.sin(angle * 2.0 + t) * np.cos(t * 0.8)
            x += oscillation * np.cos(angle)
            z += oscillation * np.sin(angle)
            
            voxels.append([x, y, z])
            
            # Color gradient: Doré (outer) → Vert (mid) → Bleu (inner)
            radius_norm = (radius - spiral_radius_inner) / (spiral_radius_outer - spiral_radius_inner)
            
            if radius_norm > 0.66:
                # Outer: Doré
                t_blend = (radius_norm - 0.66) / 0.34
                col = (1 - t_blend) * np.array([1.0, 0.84, 0.0]) + t_blend * np.array([1.0, 0.7, 0.0])
            elif radius_norm > 0.33:
                # Mid: Vert Sahara
                t_blend = (radius_norm - 0.33) / 0.33
                col = (1 - t_blend) * np.array(self.colors["vert_niger"]) + t_blend * np.array([1.0, 0.7, 0.0])
            else:
                # Inner: Bleu Nuit
                t_blend = radius_norm / 0.33
                col = (1 - t_blend) * np.array(self.colors["bleu_nuit"]) + t_blend * np.array(self.colors["vert_niger"])
            
            voxel_colors.append(col)
        
        voxels = np.array(voxels)
        voxel_colors = np.array(voxel_colors)
        
        # === MORPHING TRANSITION ===
        if morph_progress > 0:
            # Get target 22EMEEDITION positions
            target_pos, target_cols = self._phase_22eme_edition(num, t, audio_energy)
            
            # Ease-in morphing
            ease = morph_progress * morph_progress * (3.0 - 2.0 * morph_progress)
            
            pos = (1.0 - ease) * voxels + ease * target_pos
            cols = (1.0 - ease) * voxel_colors + ease * target_cols
        else:
            pos = voxels
            cols = voxel_colors
        
        # === PULSATION ON AUDIO ENERGY ===
        pulse = 0.9 + 0.1 * np.sin(t * (2.0 + audio_energy * 3.0))
        cols = cols * pulse
        
        return pos, np.clip(cols, 0, 1)


    def _phase_22eme_edition(self, num, t=0.0, audio_energy=0.5):
        """
        Advanced 3D Typography: "22EMEEDITION"
        - Chiffres "22" avec pulsation et halo doré
        - Lettres "EMEEDITION" avec gradient vert/blanc et micro-ondulations
        - Audio-réactivité : pulsations sur basses (kick), ondulations sur aigus
        """
        
        # === PART 1: "22" (Golden, Pulsing) ===
        # Each digit is a 5x7 grid voxelized
        digit_font = {
            '2': [[0,1,1,1,0],[1,0,0,0,1],[0,0,1,1,0],[0,1,0,0,0],[1,1,1,1,1]],
            '0': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        }
        
        # === PART 2: "EMEEDITION" (Letters, Gradient) ===
        letter_font = {
            'E': [[1,1,1,1,1],[1,0,0,0,0],[1,1,1,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            'M': [[1,0,0,0,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'D': [[1,1,1,0,0],[1,0,0,1,0],[1,0,0,0,1],[1,0,0,1,0],[1,1,1,0,0]],
            'I': [[0,1,1,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,1,0]],
            'T': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            'N': [[1,0,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,0,1]],
        }
        
        # Combined text: "22EMEEDITION"
        text = "22EMEEDITION"
        
        # Grid generation
        char_width = 8  # voxels wide (5 + spacing) - ENLARGED from 6
        char_height = 9  # ENLARGED from 7
        total_width = len(text) * char_width
        
        # Allocate positions and colors
        pos = np.zeros((num, 3))
        cols = np.zeros((num, 3))
        
        # Generate voxel grid for each character
        voxels = []
        voxel_colors = []
        char_idx_list = []  # Track which character each voxel belongs to
        
        for char_pos, char in enumerate(text):
            # Get font grid
            if char in digit_font:
                grid = digit_font[char]
                is_digit = True
            elif char in letter_font:
                grid = letter_font[char]
                is_digit = False
            else:
                continue
            
            # Fill grid with voxels
            base_x = char_pos * char_width - total_width / 2
            
            for row, line in enumerate(grid):
                for col, pixel in enumerate(line):
                    if pixel == 1:
                        vx = base_x + col
                        vy = 70 - row  # Y centered at 70m
                        vz = 0
                        voxels.append([vx, vy, vz])
                        voxel_colors.append((char_pos, is_digit))
                        char_idx_list.append(char_pos)
        
        # === ANIMATION LOGIC ===
        # Sample voxels uniformly across the 1000 drones
        voxels = np.array(voxels) if voxels else np.zeros((1, 3))
        voxel_colors = np.array(voxel_colors) if voxel_colors else np.array([(0, True)])
        
        if len(voxels) < num:
            # Repeat/pad if not enough voxels
            indices = np.linspace(0, len(voxels)-1, num).astype(int)
            voxels = voxels[indices]
            voxel_colors = voxel_colors[indices]
        else:
            # Sample uniformly
            indices = np.linspace(0, len(voxels)-1, num).astype(int)
            voxels = voxels[indices]
            voxel_colors = voxel_colors[indices]
        
        pos = voxels.copy()
        
        # === DIGIT ANIMATION (Pulsation + Glow) ===
        for i in range(num):
            char_pos, is_digit = voxel_colors[i]
            
            if is_digit:
                # DIGITS: Pulsation on beat (kick from audio_energy)
                pulse = 0.5 + 0.5 * np.sin(t * (2 + 4*audio_energy))  # Faster on high energy
                scale = 0.9 + 0.15 * pulse
                
                # Apply scale around character center
                char_center_x = char_pos * char_width - total_width/2 + char_width/2
                pos[i, 0] = char_center_x + (pos[i, 0] - char_center_x) * scale
                pos[i, 1] = 70 + (pos[i, 1] - 70) * scale
                
                # Color: Golden halo
                base_col = np.array([1.0, 0.84, 0.0])  # Soleil Or
                # Glow: Brighten on pulse
                cols[i] = base_col * (0.7 + 0.3 * pulse)
                
            else:
                # LETTERS: Micro-oscillations + gradient color
                
                # Micro-oscillation: Wave through letters based on X position
                wave_x = pos[i, 0] * 0.05
                oscillation_y = 2.0 * np.sin(wave_x + t * 2.0)
                oscillation_z = 1.5 * np.cos(wave_x + t * 2.0)
                
                pos[i, 1] += oscillation_y
                pos[i, 2] += oscillation_z
                
                # Color gradient: Doré (top) → Vert/Blanc (bottom)
                y_norm = (pos[i, 1] - 60) / 20  # Normalize within character height
                y_norm = np.clip(y_norm, 0, 1)
                
                if y_norm > 0.5:
                    # Top half: Orange transition
                    t_blend = (y_norm - 0.5) / 0.5
                    cols[i] = (1 - t_blend) * np.array([1.0, 0.7, 0.0]) + t_blend * np.array([1.0, 0.84, 0.0])
                else:
                    # Bottom half: Vert to Blanc
                    t_blend = y_norm / 0.5
                    cols[i] = (1 - t_blend) * np.array(self.colors["vert_niger"]) + t_blend * np.array(self.colors["blanc_pure"])
        
        # === ENTRY ANIMATION (Zoom in from beginning) ===
        # First 1 second: zoom from center
        if t < 1.0:
            entry_scale = t  # 0 → 1 over 1 second
            pos = pos * entry_scale
        
        return pos, cols

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

    def _act_5_african_soul(self, num_drones, t, audio_energy):
        """
        ACT 5: L'âme africaine - Africa Map with Niger highlighted in red.
        
        Formation phases:
        0-3s: Reveal Africa outline (white) with puzzle effect
        3-6s: Highlight Niger in red at center
        6-9s: Zoom on Niger with pulsation based on audio
        9+: Hold formation with dynamic brightness
        """
        # Pre-cached positions and colors for performance
        # Generate once and reuse
        if not hasattr(self, '_act5_cache'):
            from africa_map_generator import AfricaMapGenerator
            generator = AfricaMapGenerator(width=400, height=400, scale=0.8)
            base_pos_tmp, base_colors_tmp = generator.extract_drone_coordinates(num_drones)
            self._act5_cache = (base_pos_tmp, base_colors_tmp)
        
        base_pos, base_colors = self._act5_cache
        
        # Ensure float32 for color operations
        base_pos = base_pos.astype(np.float32)
        base_colors = base_colors.astype(np.float32)
        
        # Time progression within phase
        phase_t = t % 12.0  # 12 second cycle
        
        if phase_t < 3.0:  # === REVEAL (0-3s) ===
            # Start with full map visible, gradually brighten
            progress = phase_t / 3.0
            
            positions = base_pos.copy()
            colors = base_colors.copy()
            
            # Gradually brighten from dim to full brightness
            brightness = 0.3 + 0.7 * progress
            colors = colors * brightness
            
        elif phase_t < 6.0:  # === NIGER HIGHLIGHT (3-6s) ===
            # Emphasize Niger in red, dim rest
            progress = (phase_t - 3.0) / 3.0
            
            positions = base_pos.copy()
            colors = base_colors.copy()
            
            # Identify Niger drones (red)
            niger_mask = np.all(colors > np.array([0.8, 0, 0]), axis=1)
            
            # Brighten Niger
            colors[niger_mask] = np.array([1, 0, 0], dtype=np.float32)
            # Dim Africa outline
            colors[~niger_mask] = colors[~niger_mask] * (0.5 + 0.5 * progress)
            
        elif phase_t < 9.0:  # === ZOOM ON NIGER (6-9s) ===
            # Zoom transformation: center on Niger
            progress = (phase_t - 6.0) / 3.0
            zoom_factor = 1.0 + progress * 1.5  # Zoom up to 2.5x
            
            positions = base_pos.copy()
            colors = base_colors.copy()
            
            # Niger center (approximate)
            niger_center = np.array([0, 50, 0], dtype=np.float32)
            
            # Zoom: move drones toward Niger center
            vectors = niger_center - positions
            positions = positions + vectors * (1 - 1/zoom_factor)
            
            # Audio-reactive pulsation (beat based)
            pulsation = 0.8 + 0.2 * np.sin(audio_energy * np.pi) * np.sin(t * 3.0)
            colors = colors * pulsation
            
        else:  # === HOLD (9+s) ===
            positions = base_pos.copy()
            colors = base_colors.copy()
            
            # Audio-reactive brightness on Niger
            niger_mask = np.all(base_colors > np.array([0.8, 0, 0]), axis=1)
            
            # Pulsate red drones with audio energy
            brightness = 0.7 + 0.3 * audio_energy
            colors[niger_mask] = np.array([1, 0, 0], dtype=np.float32) * brightness
            colors[~niger_mask] = colors[~niger_mask] * (0.6 + 0.4 * audio_energy)
        
        # Ensure valid array shape and dtype
        positions = positions.astype(np.float32)
        colors = colors.astype(np.float32)
        
        if len(positions) < num_drones:
            padding = num_drones - len(positions)
            positions = np.vstack([positions, np.zeros((padding, 3), dtype=np.float32)])
            colors = np.vstack([colors, np.zeros((padding, 3), dtype=np.float32)])
        elif len(positions) > num_drones:
            positions = positions[:num_drones]
            colors = colors[:num_drones]
        
        return positions, colors
