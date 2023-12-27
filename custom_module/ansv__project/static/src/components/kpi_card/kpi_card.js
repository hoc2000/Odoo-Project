/** @odoo-module */

const { Component, onWillStart, useRef, onMounted } = owl
import { loadJS, loadCSS } from "@web/core/assets"
export class KpiCard extends Component { 
    setup() {
        onWillStart(async () => {
            // await loadCSS("https://unpkg.com/aos@2.3.1/dist/aos.css")
            // await loadJS("https://unpkg.com/aos@2.3.1/dist/aos.js")
            //for aos
            AOS.init({
                offset: 20,
            });
        })
    }
}

KpiCard.template = "owl.KpiCard"