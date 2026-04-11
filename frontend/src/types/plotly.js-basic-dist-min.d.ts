declare module 'plotly.js-basic-dist-min' {
  export type PlotlyDatum = Record<string, unknown>
  export type PlotlyLayout = Record<string, unknown>
  export type PlotlyConfig = Record<string, unknown>

  export interface PlotlyModule {
    newPlot(
      root: HTMLElement,
      data: PlotlyDatum[],
      layout?: PlotlyLayout,
      config?: PlotlyConfig,
    ): Promise<unknown>
    react(
      root: HTMLElement,
      data: PlotlyDatum[],
      layout?: PlotlyLayout,
      config?: PlotlyConfig,
    ): Promise<unknown>
    purge(root: HTMLElement): void
    Plots?: {
      resize(root: HTMLElement): void
    }
  }

  const Plotly: PlotlyModule
  export default Plotly
}
