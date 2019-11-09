<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:cb="http://www.cbeta.org/ns/1.0"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:param name="position" />
  <xsl:param name="div_type" />

  <xsl:template match="tei:body">
    <xsl:copy>
      <xsl:apply-templates select="@*" />
      <xsl:copy-of select=".//cb:div[@type=$div_type][count(ancestor::cb:div[@type=$div_type] | preceding::cb:div[@type=$div_type])=$position]" />
    </xsl:copy>
  </xsl:template>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
