<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:cb="http://www.cbeta.org/ns/1.0"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output encoding="UTF-8" method="xml" />

  <xsl:param name="position" />
  <xsl:param name="div_type" />
  <xsl:param name="treatment" />

  <xsl:template match="tei:body">
    <xsl:copy>
      <xsl:apply-templates select="@*" />
      <xsl:variable name="div" select=".//cb:div[@type=$div_type][count(ancestor::cb:div[@type=$div_type] | preceding::cb:div[@type=$div_type])=$position]" />
      <xsl:copy-of select="$div" />
      <xsl:if test="$treatment = 'merge_to_preceding'">
        <xsl:variable name="next-div" select="$div/following::cb:div[@type=$div_type][1]" />
        <xsl:if test="not(normalize-space($next-div/cb:mulu/text()))">
          <xsl:copy-of select="$next-div" />
        </xsl:if>
      </xsl:if>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
