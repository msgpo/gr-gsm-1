#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Trx radio interface
# Author: (C) Piotr Krysik 2017
# Description: Alpha version of trx radio interface
# Generated: Thu Nov 30 13:02:31 2017
##################################################

from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from grgsm import gsm_gmsk_mod
from optparse import OptionParser
import grgsm
import math
import time


class radio_if_grc(gr.top_block):

    def __init__(self, samp_rate=13e6/12.0, tx_gain=30, tx_freq=938900000, rx_freq=938600000, rx_gain=40, osr=4, ppm=-1, trx_base_port="5700", trx_remote_addr="127.0.0.1", delay_correction=285.616e-6, uplink_shift=-(6.0/1625000*(156.25)*3), timing_advance=0):
        gr.top_block.__init__(self, "Trx radio interface")

        ##################################################
        # Parameters
        ##################################################
        self.samp_rate = samp_rate
        self.tx_gain = tx_gain
        self.tx_freq = tx_freq
        self.rx_freq = rx_freq
        self.rx_gain = rx_gain
        self.osr = osr
        self.ppm = ppm
        self.trx_base_port = trx_base_port
        self.trx_remote_addr = trx_remote_addr
        self.delay_correction = delay_correction
        self.uplink_shift = uplink_shift
        self.timing_advance = timing_advance

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_clock_rate(26e6, uhd.ALL_MBOARDS)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(rx_freq, 0)
        self.uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        	"packet_len",
        )
        self.uhd_usrp_sink_0.set_clock_rate(26e6, uhd.ALL_MBOARDS)
        self.uhd_usrp_sink_0.set_subdev_spec("A:B", 0)
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(tx_freq, 0)
        self.uhd_usrp_sink_0.set_gain(tx_gain, 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.ts_filter = grgsm.burst_timeslot_filter(0)
        self.low_pass_filter_0_0 = filter.fir_filter_ccf(1, firdes.low_pass(
        	1, samp_rate, 125e3, 5e3, firdes.WIN_HAMMING, 6.76))
        self.gsm_txtime_setter_0 = grgsm.txtime_setter(None if (None is not None) else 0xffffffff, 0, 0, 0, 0, timing_advance, delay_correction+uplink_shift)
        self.gsm_trx_burst_if_0 = grgsm.trx_burst_if(trx_remote_addr, trx_base_port)
        self.gsm_receiver_0 = grgsm.receiver(4, ([0]), ([4]), False)
        self.gsm_preprocess_tx_burst_0 = grgsm.preprocess_tx_burst()
        self.gsm_msg_to_tag_0_0 = grgsm.msg_to_tag()
        self.gsm_msg_to_tag_0 = grgsm.msg_to_tag()
        self.gsm_gmsk_mod_0 = gsm_gmsk_mod(
            BT=0.3,
            pulse_duration=4,
            sps=osr,
        )
        self.gsm_gen_test_ab_0 = grgsm.gen_test_ab()
        self.gsm_controlled_rotator_cc_0_0 = grgsm.controlled_rotator_cc(-ppm/1.0e6*2*math.pi*tx_freq/samp_rate)
        self.gsm_controlled_rotator_cc_0 = grgsm.controlled_rotator_cc(ppm/1.0e6*2*math.pi*rx_freq/samp_rate)
        self.gsm_burst_type_filter_0_0 = grgsm.burst_type_filter(([1,3]))
        self.gsm_burst_type_filter_0 = grgsm.burst_type_filter(([3]))
        self.gsm_burst_to_fn_time_0 = grgsm.burst_to_fn_time()
        self.gsm_burst_timeslot_filter_0 = grgsm.burst_timeslot_filter(0)
        self.digital_burst_shaper_xx_0 = digital.burst_shaper_cc((firdes.window(firdes.WIN_HANN, 16, 0)), 0, 20, False, "packet_len")
        self.blocks_pdu_to_tagged_stream_0_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, "packet_len")

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.gsm_burst_timeslot_filter_0, 'out'), (self.gsm_gen_test_ab_0, 'bursts_in'))    
        self.msg_connect((self.gsm_burst_to_fn_time_0, 'fn_time_out'), (self.gsm_txtime_setter_0, 'fn_time'))    
        self.msg_connect((self.gsm_burst_type_filter_0, 'bursts_out'), (self.gsm_burst_to_fn_time_0, 'bursts_in'))    
        self.msg_connect((self.gsm_burst_type_filter_0_0, 'bursts_out'), (self.gsm_burst_timeslot_filter_0, 'in'))    
        self.msg_connect((self.gsm_gen_test_ab_0, 'bursts_out'), (self.gsm_txtime_setter_0, 'bursts_in'))    
        self.msg_connect((self.gsm_preprocess_tx_burst_0, 'bursts_out'), (self.blocks_pdu_to_tagged_stream_0_0, 'pdus'))    
        self.msg_connect((self.gsm_receiver_0, 'C0'), (self.gsm_burst_type_filter_0, 'bursts_in'))    
        self.msg_connect((self.gsm_receiver_0, 'C0'), (self.gsm_burst_type_filter_0_0, 'bursts_in'))    
        self.msg_connect((self.gsm_receiver_0, 'C0'), (self.ts_filter, 'in'))    
        self.msg_connect((self.gsm_trx_burst_if_0, 'bursts'), (self.gsm_txtime_setter_0, 'bursts_in'))    
        self.msg_connect((self.gsm_txtime_setter_0, 'bursts_out'), (self.gsm_preprocess_tx_burst_0, 'bursts_in'))    
        self.msg_connect((self.ts_filter, 'out'), (self.gsm_trx_burst_if_0, 'bursts'))    
        self.connect((self.blocks_pdu_to_tagged_stream_0_0, 0), (self.gsm_gmsk_mod_0, 0))    
        self.connect((self.digital_burst_shaper_xx_0, 0), (self.gsm_msg_to_tag_0_0, 0))    
        self.connect((self.gsm_controlled_rotator_cc_0, 0), (self.low_pass_filter_0_0, 0))    
        self.connect((self.gsm_controlled_rotator_cc_0_0, 0), (self.uhd_usrp_sink_0, 0))    
        self.connect((self.gsm_gmsk_mod_0, 0), (self.digital_burst_shaper_xx_0, 0))    
        self.connect((self.gsm_msg_to_tag_0, 0), (self.gsm_controlled_rotator_cc_0, 0))    
        self.connect((self.gsm_msg_to_tag_0_0, 0), (self.gsm_controlled_rotator_cc_0_0, 0))    
        self.connect((self.low_pass_filter_0_0, 0), (self.gsm_receiver_0, 0))    
        self.connect((self.uhd_usrp_source_0, 0), (self.gsm_msg_to_tag_0, 0))    

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, 125e3, 5e3, firdes.WIN_HAMMING, 6.76))
        self.gsm_controlled_rotator_cc_0.set_phase_inc(self.ppm/1.0e6*2*math.pi*self.rx_freq/self.samp_rate)
        self.gsm_controlled_rotator_cc_0_0.set_phase_inc(-self.ppm/1.0e6*2*math.pi*self.tx_freq/self.samp_rate)
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.uhd_usrp_sink_0.set_gain(self.tx_gain, 0)
        	

    def get_tx_freq(self):
        return self.tx_freq

    def set_tx_freq(self, tx_freq):
        self.tx_freq = tx_freq
        self.gsm_controlled_rotator_cc_0_0.set_phase_inc(-self.ppm/1.0e6*2*math.pi*self.tx_freq/self.samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(self.tx_freq, 0)

    def get_rx_freq(self):
        return self.rx_freq

    def set_rx_freq(self, rx_freq):
        self.rx_freq = rx_freq
        self.gsm_controlled_rotator_cc_0.set_phase_inc(self.ppm/1.0e6*2*math.pi*self.rx_freq/self.samp_rate)
        self.uhd_usrp_source_0.set_center_freq(self.rx_freq, 0)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_0.set_gain(self.rx_gain, 0)
        	

    def get_osr(self):
        return self.osr

    def set_osr(self, osr):
        self.osr = osr
        self.gsm_gmsk_mod_0.set_sps(self.osr)

    def get_ppm(self):
        return self.ppm

    def set_ppm(self, ppm):
        self.ppm = ppm
        self.gsm_controlled_rotator_cc_0.set_phase_inc(self.ppm/1.0e6*2*math.pi*self.rx_freq/self.samp_rate)
        self.gsm_controlled_rotator_cc_0_0.set_phase_inc(-self.ppm/1.0e6*2*math.pi*self.tx_freq/self.samp_rate)

    def get_trx_base_port(self):
        return self.trx_base_port

    def set_trx_base_port(self, trx_base_port):
        self.trx_base_port = trx_base_port

    def get_trx_remote_addr(self):
        return self.trx_remote_addr

    def set_trx_remote_addr(self, trx_remote_addr):
        self.trx_remote_addr = trx_remote_addr

    def get_delay_correction(self):
        return self.delay_correction

    def set_delay_correction(self, delay_correction):
        self.delay_correction = delay_correction
        self.gsm_txtime_setter_0.set_delay_correction(self.delay_correction+self.uplink_shift)

    def get_uplink_shift(self):
        return self.uplink_shift

    def set_uplink_shift(self, uplink_shift):
        self.uplink_shift = uplink_shift
        self.gsm_txtime_setter_0.set_delay_correction(self.delay_correction+self.uplink_shift)

    def get_timing_advance(self):
        return self.timing_advance

    def set_timing_advance(self, timing_advance):
        self.timing_advance = timing_advance
        self.gsm_txtime_setter_0.set_timing_advance(self.timing_advance)


def argument_parser():
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option(
        "", "--samp-rate", dest="samp_rate", type="eng_float", default=eng_notation.num_to_str(13e6/12.0),
        help="Set samp_rate [default=%default]")
    parser.add_option(
        "-r", "--tx-gain", dest="tx_gain", type="eng_float", default=eng_notation.num_to_str(30),
        help="Set tx_gain [default=%default]")
    parser.add_option(
        "-u", "--tx-freq", dest="tx_freq", type="eng_float", default=eng_notation.num_to_str(938900000),
        help="Set tx_freq [default=%default]")
    parser.add_option(
        "-d", "--rx-freq", dest="rx_freq", type="eng_float", default=eng_notation.num_to_str(938600000),
        help="Set rx_freq [default=%default]")
    parser.add_option(
        "-g", "--rx-gain", dest="rx_gain", type="eng_float", default=eng_notation.num_to_str(40),
        help="Set rx_gain [default=%default]")
    parser.add_option(
        "", "--osr", dest="osr", type="intx", default=4,
        help="Set OSR [default=%default]")
    parser.add_option(
        "", "--ppm", dest="ppm", type="eng_float", default=eng_notation.num_to_str(-1),
        help="Set Clock offset correction [default=%default]")
    parser.add_option(
        "", "--trx-base-port", dest="trx_base_port", type="string", default="5700",
        help="Set 5700 [default=%default]")
    parser.add_option(
        "", "--trx-remote-addr", dest="trx_remote_addr", type="string", default="127.0.0.1",
        help="Set 127.0.0.1 [default=%default]")
    parser.add_option(
        "", "--delay-correction", dest="delay_correction", type="eng_float", default=eng_notation.num_to_str(285.616e-6),
        help="Set delay_correction [default=%default]")
    parser.add_option(
        "", "--uplink-shift", dest="uplink_shift", type="eng_float", default=eng_notation.num_to_str(-(6.0/1625000*(156.25)*3)),
        help="Set uplink_shift [default=%default]")
    parser.add_option(
        "", "--timing-advance", dest="timing_advance", type="eng_float", default=eng_notation.num_to_str(0),
        help="Set timing_advance [default=%default]")
    return parser


def main(top_block_cls=radio_if_grc, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(samp_rate=options.samp_rate, tx_gain=options.tx_gain, tx_freq=options.tx_freq, rx_freq=options.rx_freq, rx_gain=options.rx_gain, osr=options.osr, ppm=options.ppm, trx_base_port=options.trx_base_port, trx_remote_addr=options.trx_remote_addr, delay_correction=options.delay_correction, uplink_shift=options.uplink_shift, timing_advance=options.timing_advance)
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
