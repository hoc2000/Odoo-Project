/** @odoo-module */

import { registry } from "@web/core/registry"
import { loadJS, loadCSS } from "@web/core/assets"
const { Component, onWillStart, useRef, onMounted, useEffect, onWillUnmount } = owl
import { useService } from '@web/core/utils/hooks';

export class ChartRenderer extends Component {
    setup() {
        this.chartRef = useRef("chart")
        this.actionService = useService("action")

        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js")
            // await loadJS("web/static/lib/Chart/Chart.js")
            // await loadCSS("https://unpkg.com/aos@2.3.1/dist/aos.css")
            // await loadJS("https://unpkg.com/aos@2.3.1/dist/aos.js")
        })

        onMounted(() => this.renderChart())
        onWillUnmount(() => {
            if (this.chart) {
                this.chart.destroy()
            }
        })

        useEffect(() => {
            this.renderChart()
        }, () => [this.props.config])
    }

    renderChart() {
        const old_chartjs = document.querySelector('script[src="/web/static/lib/Chart/Chart.js"]')

        if (old_chartjs) {
            return
        }

        if (this.chart) {
            this.chart.destroy()
        }

        this.chart = new Chart(this.chartRef.el,
            {
                type: this.props.type,
                data: this.props.config.data,
                options: {
                    onClick: (e) => {
                        const active = e.chart.getActiveElements()
                        if (active) {
                            const label = e.chart.data.labels[active[0].index]
                            this.actionService.doAction({
                                type: "ir.actions.act_window",
                                name: this.props.title,
                                res_model: "task.project.ansv",
                                views: [
                                    [false, "list"],
                                    [false, "kanban"],
                                    [false, "form"],
                                ]
                            })
                        }
                    },
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        title: {
                            display: true,
                            text: this.props.title,
                            position: 'bottom',
                        }
                    }
                },
            }
        );
    }
}

ChartRenderer.template = "owl.ChartRenderer"